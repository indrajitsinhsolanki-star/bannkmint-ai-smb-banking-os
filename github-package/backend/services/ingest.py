"""
CSV ingestion and normalization service for BannkMint AI
"""
import pandas as pd
import numpy as np
import chardet
import re
import hashlib
from datetime import datetime, timedelta
from dateutil import parser
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from db import Transaction, Account
import io

class CSVIngestor:
    """Handles CSV file parsing, normalization, and ingestion"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def detect_encoding(self, file_content: bytes) -> str:
        """Detect file encoding using chardet"""
        result = chardet.detect(file_content)
        return result['encoding'] or 'utf-8'
    
    def detect_delimiter(self, sample_lines: str) -> str:
        """Detect CSV delimiter by testing common options"""
        delimiters = [',', ';', '\t', '|']
        delimiter_scores = {}
        
        for delimiter in delimiters:
            try:
                df_test = pd.read_csv(io.StringIO(sample_lines), delimiter=delimiter, nrows=5)
                # Score based on number of columns and consistency
                if len(df_test.columns) > 1:
                    delimiter_scores[delimiter] = len(df_test.columns)
            except:
                delimiter_scores[delimiter] = 0
                
        # Return delimiter with highest score
        best_delimiter = max(delimiter_scores, key=delimiter_scores.get)
        return best_delimiter if delimiter_scores[best_delimiter] > 1 else ','
    
    def normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to standard format"""
        column_mapping = {
            # Date columns
            'date': ['date', 'transaction date', 'posted date', 'trans date', 'effective date'],
            'description': ['description', 'memo', 'payee', 'merchant', 'details', 'transaction details'],
            'amount': ['amount', 'transaction amount', 'debit', 'credit', 'value', 'sum'],
            'balance': ['balance', 'running balance', 'account balance', 'current balance'],
            'currency': ['currency', 'curr', 'ccy']
        }
        
        # Convert to lowercase for matching
        df.columns = df.columns.str.lower().str.strip()
        
        # Map columns
        mapped_columns = {}
        for standard_name, variations in column_mapping.items():
            for col in df.columns:
                for variation in variations:
                    if variation in col:
                        mapped_columns[col] = standard_name
                        break
                if col in mapped_columns:
                    break
        
        # Rename columns
        df = df.rename(columns=mapped_columns)
        
        # If we have separate debit/credit columns, combine them
        if 'debit' in df.columns and 'credit' in df.columns:
            # Convert debit and credit to numeric, handling various formats
            df['debit'] = df['debit'].apply(lambda x: self.parse_amount_value(x) if pd.notna(x) else 0.0)
            df['credit'] = df['credit'].apply(lambda x: self.parse_amount_value(x) if pd.notna(x) else 0.0)
            df['amount'] = df['credit'] - df['debit']  # Credit positive, debit negative
            df = df.drop(['debit', 'credit'], axis=1)
        
        return df
    
    def parse_amount_value(self, value):
        """Parse individual amount value"""
        if pd.isna(value) or value == '':
            return 0.0
            
        # Convert to string
        amount_str = str(value).strip()
        
        # Handle parentheses (negative amounts)
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = '-' + amount_str[1:-1]
        
        # Remove currency symbols and commas
        amount_str = re.sub(r'[$€£¥,\s]', '', amount_str)
        
        # Handle European decimal format (1.234,56 -> 1234.56)
        if ',' in amount_str and '.' in amount_str:
            # Check if comma is likely decimal separator
            if amount_str.rfind(',') > amount_str.rfind('.'):
                amount_str = amount_str.replace('.', '').replace(',', '.')
            else:
                amount_str = amount_str.replace(',', '')
        elif ',' in amount_str:
            # Check if comma is likely decimal separator
            comma_pos = amount_str.rfind(',')
            if len(amount_str) - comma_pos - 1 == 2:  # Two digits after comma
                amount_str = amount_str.replace(',', '.')
            else:
                amount_str = amount_str.replace(',', '')
        
        try:
            return float(amount_str)
        except (ValueError, TypeError):
            return 0.0
    
    def normalize_amounts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize amount values handling various formats"""
        if 'amount' not in df.columns:
            return df
            
        df['amount'] = df['amount'].apply(self.parse_amount_value)
        
        # Also normalize balance if it exists
        if 'balance' in df.columns:
            df['balance'] = df['balance'].apply(self.parse_amount_value)
        
        return df
    
    def normalize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize date values to datetime objects"""
        if 'date' not in df.columns:
            return df
            
        def parse_date(date_str):
            if pd.isna(date_str):
                return None
                
            try:
                # Try pandas to_datetime first
                return pd.to_datetime(date_str, errors='coerce')
            except:
                try:
                    # Try dateutil parser as fallback
                    return parser.parse(str(date_str))
                except:
                    return None
        
        df['date'] = df['date'].apply(parse_date)
        # Remove rows with invalid dates
        df = df.dropna(subset=['date'])
        
        return df
    
    def generate_transaction_hash(self, row: pd.Series) -> str:
        """Generate hash for deduplication"""
        # Normalize description for hashing
        desc = re.sub(r'\s+', ' ', str(row.get('description', '')).lower().strip())
        
        # Create hash from key fields
        hash_string = f"{row.get('date', '')}{desc}{row.get('amount', 0)}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def detect_transfers(self, df: pd.DataFrame, account_id: str) -> pd.DataFrame:
        """Detect internal transfers between accounts"""
        # For now, mark potential transfers based on description patterns
        transfer_patterns = [
            r'transfer.*to',
            r'transfer.*from', 
            r'internal.*transfer',
            r'account.*transfer',
            r'online.*transfer'
        ]
        
        df['is_transfer'] = 0
        
        for pattern in transfer_patterns:
            mask = df['description'].str.contains(pattern, case=False, na=False)
            df.loc[mask, 'is_transfer'] = 1
            df.loc[mask, 'category'] = 'Internal Transfer'
        
        return df
    
    def deduplicate_transactions(self, df: pd.DataFrame, account_id: str) -> pd.DataFrame:
        """Remove duplicate transactions"""
        # Add hash column
        df['raw_hash'] = df.apply(self.generate_transaction_hash, axis=1)
        
        # Check against existing transactions in database
        existing_hashes = set()
        existing_txns = self.db.query(Transaction).filter(
            Transaction.account_id == account_id
        ).all()
        
        for txn in existing_txns:
            existing_hashes.add(txn.raw_hash)
        
        # Remove duplicates from current dataset
        df = df.drop_duplicates(subset=['raw_hash'])
        
        # Remove transactions that already exist in database
        df = df[~df['raw_hash'].isin(existing_hashes)]
        
        return df
    
    def process_csv_file(self, file_content: bytes, account_id: str, filename: str) -> Dict:
        """Main processing pipeline for CSV files"""
        try:
            # Detect encoding
            encoding = self.detect_encoding(file_content)
            
            # Decode file content
            text_content = file_content.decode(encoding)
            
            # Detect delimiter
            delimiter = self.detect_delimiter(text_content[:1000])  # Use first 1000 chars for detection
            
            # Read CSV
            df = pd.read_csv(io.StringIO(text_content), delimiter=delimiter)
            
            if df.empty:
                return {'success': False, 'error': 'Empty CSV file'}
            
            original_count = len(df)
            
            # Normalize columns
            df = self.normalize_column_names(df)
            
            # Validate required columns
            required_columns = ['date', 'description', 'amount']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return {
                    'success': False, 
                    'error': f'Missing required columns: {missing_columns}',
                    'suggestion': 'CSV should have columns for date, description, and amount'
                }
            
            # Normalize data
            df = self.normalize_dates(df)
            df = self.normalize_amounts(df)
            
            # Add metadata
            df['account_id'] = account_id
            df['source'] = filename
            if 'currency' not in df.columns:
                df['currency'] = 'USD'
            else:
                df['currency'] = df['currency'].fillna('USD')
            
            # Detect transfers
            df = self.detect_transfers(df, account_id)
            
            # Deduplicate
            df = self.deduplicate_transactions(df, account_id)
            
            processed_count = len(df)
            skipped_count = original_count - processed_count
            
            # Convert to transaction objects and save
            transactions = []
            for _, row in df.iterrows():
                transaction = Transaction(
                    account_id=account_id,
                    posted_at=row['date'],
                    description=str(row['description'])[:500],  # Limit description length
                    amount=float(row['amount']),
                    currency=str(row.get('currency', 'USD')),
                    balance=float(row['balance']) if pd.notna(row.get('balance')) else None,
                    raw_hash=row['raw_hash'],
                    source=filename,
                    category=row.get('category'),
                    is_transfer=int(row.get('is_transfer', 0))
                )
                transactions.append(transaction)
            
            # Bulk insert
            self.db.add_all(transactions)
            self.db.commit()
            
            return {
                'success': True,
                'imported': processed_count,
                'skipped': skipped_count,
                'total_processed': original_count,
                'encoding_detected': encoding,
                'delimiter_detected': delimiter
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                'success': False,
                'error': str(e),
                'suggestion': 'Please check file format and try again'
            }
    
    def get_account_or_create_default(self) -> str:
        """Get default account or create one"""
        account = self.db.query(Account).first()
        if not account:
            account = Account(
                name="Default Account",
                institution="Unknown",
                currency="USD"
            )
            self.db.add(account)
            self.db.commit()
        return account.id