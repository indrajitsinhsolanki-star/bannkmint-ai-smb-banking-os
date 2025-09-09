"""
CSV ingestion and normalization service for BannkMint AI
Enhanced with robust parsing and deduplication
"""

import pandas as pd
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib
import uuid
from io import StringIO
from db import execute_query, get_or_create_account, generate_id
from .categorize import categorization_service

class IngestionService:
    """Enhanced CSV ingestion with intelligent parsing and deduplication"""
    
    def __init__(self):
        # Common CSV headers and their mappings
        self.header_mappings = {
            'date': ['date', 'transaction_date', 'posting_date', 'effective_date', 'trans_date'],
            'description': ['description', 'memo', 'payee', 'reference', 'details', 'transaction_details'],
            'amount': ['amount', 'transaction_amount', 'debit_credit', 'net_amount'],
            'debit': ['debit', 'debit_amount', 'withdrawal', 'outgoing'],
            'credit': ['credit', 'credit_amount', 'deposit', 'incoming'],
            'balance': ['balance', 'running_balance', 'account_balance'],
            'category': ['category', 'type', 'transaction_type', 'classification']
        }
        
        # Date format patterns to try
        self.date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d-%m-%Y', '%b %d, %Y', '%B %d, %Y',
            '%m/%d/%y', '%d/%m/%y', '%y-%m-%d'
        ]
    
    def process_csv_upload(
        self, 
        csv_content: str, 
        account_name: str = "Default Account",
        account_type: str = "checking"
    ) -> Dict[str, Any]:
        """
        Process uploaded CSV with intelligent parsing and categorization
        """
        try:
            # Step 1: Parse CSV content
            df = self._parse_csv_content(csv_content)
            
            if df.empty:
                return {
                    "success": False,
                    "error": "CSV file is empty or invalid",
                    "processed_count": 0
                }
            
            # Step 2: Normalize column headers
            df = self._normalize_headers(df)
            
            # Step 3: Validate required columns
            validation_result = self._validate_required_columns(df)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "detected_headers": list(df.columns),
                    "processed_count": 0
                }
            
            # Step 4: Clean and normalize data
            df = self._clean_and_normalize_data(df)
            
            # Step 5: Get or create account
            account_id = get_or_create_account(account_name, account_type)
            
            # Step 6: Deduplicate transactions
            df, duplicate_count = self._deduplicate_transactions(df, account_id)
            
            # Step 7: Categorize transactions
            df = self._categorize_transactions(df)
            
            # Step 8: Insert into database
            inserted_count = self._insert_transactions(df, account_id)
            
            # Step 9: Update account balance
            self._update_account_balance(account_id, df)
            
            return {
                "success": True,
                "account_id": account_id,
                "processed_count": inserted_count,
                "duplicate_count": duplicate_count,
                "total_rows": len(df) + duplicate_count,
                "date_range": {
                    "earliest": df['date'].min().isoformat() if not df.empty else None,
                    "latest": df['date'].max().isoformat() if not df.empty else None
                },
                "amount_summary": {
                    "total_credits": float(df[df['amount'] > 0]['amount'].sum()) if not df.empty else 0,
                    "total_debits": float(df[df['amount'] < 0]['amount'].sum()) if not df.empty else 0,
                    "net_amount": float(df['amount'].sum()) if not df.empty else 0
                },
                "categories_detected": df['category'].value_counts().to_dict() if 'category' in df.columns else {}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Processing error: {str(e)}",
                "processed_count": 0
            }
    
    def _parse_csv_content(self, csv_content: str) -> pd.DataFrame:
        """Parse CSV content with various delimiters and encodings"""
        # Try different delimiters
        delimiters = [',', ';', '\t', '|']
        
        for delimiter in delimiters:
            try:
                # Try reading with current delimiter
                df = pd.read_csv(
                    StringIO(csv_content),
                    delimiter=delimiter,
                    encoding='utf-8',
                    skipinitialspace=True,
                    na_values=['', 'NULL', 'null', 'N/A', 'n/a'],
                    keep_default_na=True
                )
                
                # Check if we got meaningful columns (more than 1 column with data)
                if len(df.columns) > 1 and not df.empty:
                    return df
                    
            except Exception:
                continue
        
        # If all delimiters fail, try a more lenient approach
        try:
            df = pd.read_csv(
                StringIO(csv_content),
                sep=None,  # Let pandas detect separator
                engine='python',
                encoding='utf-8',
                skipinitialspace=True
            )
            return df
        except Exception:
            return pd.DataFrame()
    
    def _normalize_headers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column headers to standard format"""
        header_map = {}
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            
            # Find the best match for this column
            for standard_name, variations in self.header_mappings.items():
                if any(variation in col_lower for variation in variations):
                    header_map[col] = standard_name
                    break
            
            # If no match found, keep original but cleaned
            if col not in header_map:
                header_map[col] = re.sub(r'[^\w\s]', '', col_lower).replace(' ', '_')
        
        df = df.rename(columns=header_map)
        return df
    
    def _validate_required_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate that required columns are present"""
        required_columns = ['date', 'description']
        
        # Check for amount column or debit/credit columns
        has_amount = 'amount' in df.columns
        has_debit_credit = 'debit' in df.columns and 'credit' in df.columns
        
        if not (has_amount or has_debit_credit):
            return {
                "valid": False,
                "error": "CSV must contain either 'amount' column or both 'debit' and 'credit' columns"
            }
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return {
                "valid": False,
                "error": f"Missing required columns: {', '.join(missing_columns)}"
            }
        
        return {"valid": True}
    
    def _clean_and_normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize transaction data"""
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Clean date column
        df['date'] = self._parse_dates(df['date'])
        
        # Handle amount calculation
        if 'amount' not in df.columns:
            # Calculate amount from debit/credit
            df['debit'] = pd.to_numeric(df.get('debit', 0), errors='coerce').fillna(0)
            df['credit'] = pd.to_numeric(df.get('credit', 0), errors='coerce').fillna(0)
            df['amount'] = df['credit'] - df['debit']
        else:
            # Clean existing amount column
            df['amount'] = self._clean_amount_column(df['amount'])
        
        # Clean description
        df['description'] = df['description'].astype(str).str.strip()
        df['description'] = df['description'].replace('nan', '')
        
        # Remove rows with invalid data
        df = df.dropna(subset=['date', 'description'])
        df = df[df['description'] != '']
        df = df[df['amount'] != 0]  # Remove zero-amount transactions
        
        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    def _parse_dates(self, date_series: pd.Series) -> pd.Series:
        """Parse dates using multiple format attempts"""
        parsed_dates = pd.Series(index=date_series.index, dtype='datetime64[ns]')
        
        for idx, date_val in date_series.items():
            if pd.isna(date_val):
                continue
                
            date_str = str(date_val).strip()
            
            # Try each date format
            for date_format in self.date_formats:
                try:
                    parsed_date = pd.to_datetime(date_str, format=date_format)
                    parsed_dates.iloc[idx] = parsed_date
                    break
                except (ValueError, TypeError):
                    continue
            
            # If no format worked, try pandas' automatic parsing
            if pd.isna(parsed_dates.iloc[idx]):
                try:
                    parsed_dates.iloc[idx] = pd.to_datetime(date_str, infer_datetime_format=True)
                except:
                    pass
        
        return parsed_dates
    
    def _clean_amount_column(self, amount_series: pd.Series) -> pd.Series:
        """Clean and convert amount column to numeric"""
        # Convert to string and clean
        cleaned = amount_series.astype(str)
        
        # Remove common currency symbols and formatting
        cleaned = cleaned.str.replace(r'[$£€¥₹,\s]', '', regex=True)
        
        # Handle parentheses as negative (accounting format)
        mask = cleaned.str.contains(r'\(.*\)', regex=True, na=False)
        cleaned.loc[mask] = '-' + cleaned.loc[mask].str.replace(r'[()]', '', regex=True)
        
        # Convert to numeric
        return pd.to_numeric(cleaned, errors='coerce').fillna(0)
    
    def _deduplicate_transactions(self, df: pd.DataFrame, account_id: str) -> Tuple[pd.DataFrame, int]:
        """Remove duplicate transactions based on hash matching"""
        if df.empty:
            return df, 0
        
        # Create transaction hashes
        df['transaction_hash'] = df.apply(self._create_transaction_hash, axis=1)
        
        # Get existing transaction hashes from database
        existing_hashes = set()
        try:
            existing_transactions = execute_query(
                "SELECT DISTINCT date || '|' || description || '|' || CAST(amount AS TEXT) as hash_key FROM transactions WHERE account_id = ?",
                (account_id,)
            )
            existing_hashes = {self._create_hash_from_db_row(row) for row in existing_transactions}
        except:
            pass
        
        # Filter out duplicates
        initial_count = len(df)
        df = df[~df['transaction_hash'].isin(existing_hashes)]
        duplicate_count = initial_count - len(df)
        
        # Remove duplicates within the current dataset
        df = df.drop_duplicates(subset=['transaction_hash'])
        
        return df, duplicate_count
    
    def _create_transaction_hash(self, row) -> str:
        """Create a hash for duplicate detection"""
        # Use date, description, and amount for hash
        hash_string = f"{row['date'].date()}|{row['description']}|{row['amount']}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _create_hash_from_db_row(self, row) -> str:
        """Create hash from database row for comparison"""
        return hashlib.md5(row['hash_key'].encode()).hexdigest()
    
    def _categorize_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categorize transactions using the categorization service"""
        if df.empty:
            return df
        
        df['category'] = ''
        df['confidence'] = 0.0
        df['explanation'] = ''
        
        for idx, row in df.iterrows():
            category, confidence, explanation = categorization_service.categorize_transaction(
                row['description'], 
                row['amount']
            )
            
            df.at[idx, 'category'] = category
            df.at[idx, 'confidence'] = confidence
            df.at[idx, 'explanation'] = explanation
        
        return df
    
    def _insert_transactions(self, df: pd.DataFrame, account_id: str) -> int:
        """Insert transactions into database"""
        if df.empty:
            return 0
        
        inserted_count = 0
        
        for idx, row in df.iterrows():
            try:
                transaction_id = generate_id()
                
                execute_query(
                    """INSERT INTO transactions 
                       (id, account_id, date, description, amount, category, confidence, explanation, original_csv_row) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        transaction_id,
                        account_id,
                        row['date'].isoformat(),
                        row['description'],
                        float(row['amount']),
                        row.get('category', ''),
                        float(row.get('confidence', 0.0)),
                        row.get('explanation', ''),
                        int(idx)
                    )
                )
                inserted_count += 1
                
            except Exception as e:
                print(f"Error inserting transaction {idx}: {e}")
                continue
        
        return inserted_count
    
    def _update_account_balance(self, account_id: str, df: pd.DataFrame):
        """Update account balance based on transaction amounts"""
        if df.empty:
            return
        
        # Calculate total change from this upload
        total_change = float(df['amount'].sum())
        
        # Update account balance
        try:
            execute_query(
                "UPDATE accounts SET balance = balance + ? WHERE id = ?",
                (total_change, account_id)
            )
        except Exception as e:
            print(f"Error updating account balance: {e}")
    
    def get_upload_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent upload history"""
        try:
            # Get upload summary by grouping transactions by creation date
            uploads = execute_query(f"""
                SELECT 
                    a.name as account_name,
                    DATE(t.created_at) as upload_date,
                    COUNT(*) as transaction_count,
                    SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END) as total_credits,
                    SUM(CASE WHEN t.amount < 0 THEN t.amount ELSE 0 END) as total_debits,
                    MIN(t.date) as earliest_transaction,
                    MAX(t.date) as latest_transaction
                FROM transactions t
                JOIN accounts a ON t.account_id = a.id
                GROUP BY a.name, DATE(t.created_at)
                ORDER BY upload_date DESC
                LIMIT {limit}
            """)
            
            return [
                {
                    "account_name": upload['account_name'],
                    "upload_date": upload['upload_date'],
                    "transaction_count": upload['transaction_count'],
                    "total_credits": float(upload['total_credits']),
                    "total_debits": float(upload['total_debits']),
                    "net_amount": float(upload['total_credits']) + float(upload['total_debits']),
                    "date_range": {
                        "earliest": upload['earliest_transaction'],
                        "latest": upload['latest_transaction']
                    }
                }
                for upload in uploads
            ]
            
        except Exception as e:
            print(f"Error getting upload history: {e}")
            return []

# Initialize service
ingestion_service = IngestionService()

# For backward compatibility with server.py
CSVIngestor = IngestionService