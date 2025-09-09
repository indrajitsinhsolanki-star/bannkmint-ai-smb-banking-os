"""
Banking Integration Service for BannkMint AI SMB Banking OS
Simulates bank connections, provides executive overview, generates month-end data
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from db import Transaction, Account

class BankingIntegrationService:
    """
    Banking Integration Foundation for SMB-focused banking OS
    Provides bank connection simulation and executive financial overview
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def simulate_bank_connection(self, bank_id: str, business_name: str) -> Dict[str, Any]:
        """
        Simulate OAuth bank connection flow
        In production, this would integrate with Plaid, Yodlee, or bank APIs
        """
        
        # Supported bank simulation
        supported_banks = {
            'chase_business': {
                'name': 'Chase Business Complete Banking',
                'institution': 'JPMorgan Chase Bank',
                'accounts': ['Main Business Checking', 'Business Savings', 'Business Credit Line']
            },
            'wells_fargo_business': {
                'name': 'Wells Fargo Business Choice Checking', 
                'institution': 'Wells Fargo Bank',
                'accounts': ['Business Checking', 'Merchant Services Account']
            },
            'bank_of_america_business': {
                'name': 'Bank of America Business Advantage',
                'institution': 'Bank of America', 
                'accounts': ['Business Checking', 'Business Savings']
            },
            'mercury_banking': {
                'name': 'Mercury Business Banking',
                'institution': 'Mercury Financial',
                'accounts': ['Startup Checking', 'Treasury Account']
            }
        }
        
        if bank_id not in supported_banks:
            return {
                'success': False,
                'error': f'Bank {bank_id} not supported',
                'supported_banks': list(supported_banks.keys())
            }
        
        bank_info = supported_banks[bank_id]
        
        # Create simulated accounts
        created_accounts = []
        for account_name in bank_info['accounts']:
            # Check if account already exists
            existing_account = self.db.query(Account).filter(
                Account.name == account_name,
                Account.institution == bank_info['institution']
            ).first()
            
            if not existing_account:
                new_account = Account(
                    name=account_name,
                    institution=bank_info['institution'],
                    currency='USD'
                )
                self.db.add(new_account)
                self.db.flush()  # Get the ID
                
                # Generate some sample transactions for the new account
                self._generate_sample_transactions(new_account.id, account_name)
                
                created_accounts.append({
                    'account_id': new_account.id,
                    'account_name': account_name,
                    'account_type': self._infer_account_type(account_name)
                })
        
        self.db.commit()
        
        return {
            'success': True,
            'bank_id': bank_id,
            'bank_name': bank_info['name'],
            'institution': bank_info['institution'],
            'connected_accounts': created_accounts,
            'connection_status': 'active',
            'last_sync': datetime.now().isoformat(),
            'message': f'Successfully connected to {bank_info["name"]} for {business_name}'
        }
    
    def _generate_sample_transactions(self, account_id: str, account_name: str):
        """Generate realistic sample transactions for demonstration"""
        
        # Determine account type for appropriate transactions
        account_type = self._infer_account_type(account_name)
        
        # Generate transactions for the last 60 days
        start_date = datetime.now() - timedelta(days=60)
        end_date = datetime.now()
        
        current_date = start_date
        running_balance = self._get_initial_balance(account_type)
        
        while current_date <= end_date:
            # Generate transactions based on account type and day
            if self._should_generate_transaction(current_date, account_type):
                # Get transaction template
                txn_templates = self._get_transaction_templates(account_type)
                if txn_templates:
                    template = random.choice(txn_templates)
                    
                    # Add some variance to amount
                    base_amount = template['amount']
                    variance = abs(base_amount) * 0.1  # 10% variance
                    actual_amount = base_amount + random.uniform(-variance, variance)
                    actual_amount = round(actual_amount, 2)
                    
                    # Update running balance
                    running_balance += actual_amount
                    
                    # Create transaction
                    transaction = Transaction(
                        account_id=account_id,
                        posted_at=current_date,
                        description=template['description'],
                        amount=actual_amount,
                        currency='USD',
                        balance=round(running_balance, 2),
                        source='bank_simulation',
                        category=template.get('category'),
                        vendor=template.get('vendor'),
                        confidence=0.95,
                        why='bank_data'
                    )
                    
                    self.db.add(transaction)
            
            current_date += timedelta(days=1)
    
    def _get_initial_balance(self, account_type: str) -> float:
        """Get appropriate initial balance for account type"""
        initial_balances = {
            'checking': random.uniform(15000, 50000),
            'savings': random.uniform(25000, 100000),
            'credit_line': random.uniform(-10000, 0),  # Negative for credit line
            'credit_card': random.uniform(-5000, 0),   # Negative for credit card
            'merchant_services': random.uniform(2000, 8000)
        }
        
        return round(initial_balances.get(account_type, 20000), 2)
    
    def _get_transaction_templates(self, account_type: str) -> List[Dict]:
        """Get transaction templates based on account type"""
        
        # Common business transactions
        common_business_transactions = [
            # Revenue
            {'description': 'Client Payment - Invoice #1234', 'amount': 2500.00, 'category': 'Revenue', 'vendor': 'Client'},
            {'description': 'Subscription Revenue', 'amount': 1200.00, 'category': 'Revenue', 'vendor': 'Subscription'},
            {'description': 'Consulting Services Payment', 'amount': 3500.00, 'category': 'Revenue', 'vendor': 'Consulting'},
            
            # Operating Expenses
            {'description': 'AWS Services', 'amount': -89.50, 'category': 'Software & Technology', 'vendor': 'AWS'},
            {'description': 'Google Workspace', 'amount': -24.00, 'category': 'Software & Technology', 'vendor': 'Google'},
            {'description': 'Office Rent', 'amount': -2800.00, 'category': 'Rent & Utilities', 'vendor': 'Property Management'},
            {'description': 'Internet Service', 'amount': -120.00, 'category': 'Utilities', 'vendor': 'Telecom'},
            {'description': 'Electric Bill', 'amount': -180.00, 'category': 'Utilities', 'vendor': 'Electric Company'},
            
            # Payroll
            {'description': 'Gusto Payroll Processing', 'amount': -4250.00, 'category': 'Payroll', 'vendor': 'Gusto'},
            {'description': 'Employee Benefits', 'amount': -650.00, 'category': 'Payroll', 'vendor': 'Benefits'},
            
            # Marketing
            {'description': 'Google Ads Campaign', 'amount': -450.00, 'category': 'Marketing & Advertising', 'vendor': 'Google Ads'},
            {'description': 'LinkedIn Advertising', 'amount': -280.00, 'category': 'Marketing & Advertising', 'vendor': 'LinkedIn'},
            
            # Professional Services
            {'description': 'Legal Services', 'amount': -750.00, 'category': 'Professional Services', 'vendor': 'Law Firm'},
            {'description': 'Accounting Services', 'amount': -425.00, 'category': 'Professional Services', 'vendor': 'CPA'},
            
            # Banking & Fees
            {'description': 'Bank Service Fee', 'amount': -25.00, 'category': 'Banking Fees', 'vendor': 'Bank Fee'},
            {'description': 'Wire Transfer Fee', 'amount': -15.00, 'category': 'Banking Fees', 'vendor': 'Wire Fee'},
            
            # Payment Processing
            {'description': 'Stripe Processing Fees', 'amount': -67.80, 'category': 'Payment Processing Fees', 'vendor': 'Stripe'},
            {'description': 'PayPal Transaction Fees', 'amount': -42.50, 'category': 'Payment Processing Fees', 'vendor': 'PayPal'},
            
            # Insurance
            {'description': 'Business Insurance Premium', 'amount': -340.00, 'category': 'Insurance', 'vendor': 'Insurance Co'},
            {'description': 'Workers Compensation', 'amount': -180.00, 'category': 'Insurance', 'vendor': 'Workers Comp'},
            
            # Office & Supplies
            {'description': 'Office Supplies - Staples', 'amount': -125.00, 'category': 'Office Supplies', 'vendor': 'Staples'},
            {'description': 'Business Cards Printing', 'amount': -85.00, 'category': 'Office Supplies', 'vendor': 'Print Shop'}
        ]
        
        if account_type == 'savings':
            # Savings accounts have mostly transfers and interest
            return [
                {'description': 'Transfer from Checking', 'amount': 5000.00, 'category': 'Internal Transfer', 'vendor': 'Transfer'},
                {'description': 'Interest Payment', 'amount': 15.50, 'category': 'Interest Income', 'vendor': 'Interest'},
                {'description': 'Transfer to Checking', 'amount': -2000.00, 'category': 'Internal Transfer', 'vendor': 'Transfer'},
            ]
        elif account_type == 'credit_line':
            # Credit lines have draws and payments
            return [
                {'description': 'Line of Credit Draw', 'amount': -5000.00, 'category': 'Line of Credit', 'vendor': 'Credit Draw'},
                {'description': 'Line of Credit Payment', 'amount': 1500.00, 'category': 'Loan Payment', 'vendor': 'Payment'},
                {'description': 'Line of Credit Interest', 'amount': -85.00, 'category': 'Banking Fees', 'vendor': 'Interest Charge'},
                {'description': 'Credit Line Payment', 'amount': 2000.00, 'category': 'Loan Payment', 'vendor': 'Payment'},
            ]
        elif account_type == 'credit_card':
            # Credit cards have business expenses
            return [t for t in common_business_transactions if t['amount'] < 0 and abs(t['amount']) < 2000]
        
        return common_business_transactions
    
    def _should_generate_transaction(self, date: datetime, account_type: str) -> bool:
        """Determine if a transaction should be generated on this date"""
        
        # Skip weekends for most business transactions
        if date.weekday() >= 5 and account_type not in ['credit_card', 'savings']:  # Saturday = 5, Sunday = 6
            return random.random() < 0.2  # 20% chance on weekends
        
        # Different frequencies for different account types
        probabilities = {
            'checking': 0.7,      # High activity checking account
            'savings': 0.1,       # Low activity savings
            'credit_line': 0.05,  # Occasional credit line usage
            'credit_card': 0.4,   # Moderate credit card usage
            'merchant_services': 0.8  # High activity merchant account
        }
        
        return random.random() < probabilities.get(account_type, 0.3)
    
    def get_connected_banks(self) -> List[Dict]:
        """Get all simulated bank connections"""
        # In real implementation, this would query a bank_connections table
        # For simulation, return mock data based on existing accounts
        
        accounts = self.db.query(Account).all()
        
        # Group accounts by institution
        institutions = {}
        for account in accounts:
            inst = account.institution
            if inst not in institutions:
                institutions[inst] = {
                    'institution': inst,
                    'connection_status': 'active',
                    'last_sync': datetime.now().isoformat(),
                    'accounts': []
                }
            
            # Get latest transaction for balance
            latest_txn = self.db.query(Transaction).filter(
                Transaction.account_id == account.id
            ).order_by(desc(Transaction.posted_at)).first()
            
            current_balance = latest_txn.balance if latest_txn and latest_txn.balance else 0.0
            
            institutions[inst]['accounts'].append({
                'account_id': account.id,
                'account_name': account.name,
                'account_type': self._infer_account_type(account.name),
                'current_balance': current_balance,
                'currency': account.currency
            })
        
        return list(institutions.values())
    
    def _infer_account_type(self, account_name: str) -> str:
        """Infer account type from account name"""
        name_lower = account_name.lower()
        if 'checking' in name_lower:
            return 'checking'
        elif 'savings' in name_lower:
            return 'savings'
        elif 'credit' in name_lower:
            return 'credit_line'
        elif 'merchant' in name_lower:
            return 'merchant_services'
        else:
            return 'checking'  # Default
    
    def get_financial_overview(self) -> Dict[str, Any]:
        """
        Generate executive financial overview dashboard data
        """
        # Get all accounts and their current balances
        accounts = self.db.query(Account).all()
        
        total_cash = 0.0
        total_debt = 0.0
        account_summaries = []
        
        for account in accounts:
            # Get latest balance
            latest_txn = self.db.query(Transaction).filter(
                Transaction.account_id == account.id
            ).order_by(desc(Transaction.posted_at)).first()
            
            current_balance = latest_txn.balance if latest_txn and latest_txn.balance else 0.0
            
            if current_balance >= 0:
                total_cash += current_balance
            else:
                total_debt += abs(current_balance)
            
            account_summaries.append({
                'account_id': account.id,
                'account_name': account.name,
                'institution': account.institution,
                'current_balance': current_balance,
                'account_type': self._infer_account_type(account.name)
            })
        
        # Calculate monthly metrics
        monthly_metrics = self._calculate_monthly_metrics()
        
        # Get recent activity
        recent_activity = self._get_recent_activity(limit=10)
        
        return {
            'overview': {
                'total_cash': round(total_cash, 2),
                'total_debt': round(total_debt, 2),
                'net_worth': round(total_cash - total_debt, 2),
                'total_accounts': len(accounts)
            },
            'accounts': account_summaries,
            'monthly_metrics': monthly_metrics,
            'recent_activity': recent_activity,
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_monthly_metrics(self) -> Dict[str, Any]:
        """Calculate this month vs last month financial metrics"""
        
        # Current month
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Last month  
        if current_month_start.month == 1:
            last_month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
        else:
            last_month_start = current_month_start.replace(month=current_month_start.month - 1)
        
        # Current month transactions
        current_month_txns = self.db.query(Transaction).filter(
            Transaction.posted_at >= current_month_start
        ).all()
        
        # Last month transactions
        last_month_txns = self.db.query(Transaction).filter(
            and_(
                Transaction.posted_at >= last_month_start,
                Transaction.posted_at < current_month_start
            )
        ).all()
        
        # Calculate metrics
        current_revenue = sum(t.amount for t in current_month_txns if t.amount > 0)
        current_expenses = sum(abs(t.amount) for t in current_month_txns if t.amount < 0)
        
        last_revenue = sum(t.amount for t in last_month_txns if t.amount > 0)
        last_expenses = sum(abs(t.amount) for t in last_month_txns if t.amount < 0)
        
        # Calculate growth rates
        revenue_growth = ((current_revenue - last_revenue) / last_revenue * 100) if last_revenue > 0 else 0
        expense_growth = ((current_expenses - last_expenses) / last_expenses * 100) if last_expenses > 0 else 0
        
        return {
            'current_month': {
                'revenue': round(current_revenue, 2),
                'expenses': round(current_expenses, 2),
                'net_income': round(current_revenue - current_expenses, 2),
                'transaction_count': len(current_month_txns)
            },
            'last_month': {
                'revenue': round(last_revenue, 2),
                'expenses': round(last_expenses, 2),
                'net_income': round(last_revenue - last_expenses, 2),
                'transaction_count': len(last_month_txns)
            },
            'growth': {
                'revenue_growth_pct': round(revenue_growth, 1),
                'expense_growth_pct': round(expense_growth, 1),
                'net_income_growth_pct': round(((current_revenue - current_expenses) - (last_revenue - last_expenses)) / (last_revenue - last_expenses) * 100, 1) if (last_revenue - last_expenses) != 0 else 0
            }
        }
    
    def _get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Get recent transaction activity"""
        
        recent_txns = self.db.query(Transaction).order_by(
            desc(Transaction.posted_at)
        ).limit(limit).all()
        
        activity = []
        for txn in recent_txns:
            account = self.db.query(Account).filter(Account.id == txn.account_id).first()
            
            activity.append({
                'transaction_id': txn.id,
                'date': txn.posted_at.isoformat(),
                'description': txn.description,
                'amount': txn.amount,
                'category': txn.category,
                'vendor': txn.vendor,
                'account_name': account.name if account else 'Unknown Account'
            })
        
        return activity