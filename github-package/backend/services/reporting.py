"""
Month-End Reporting Framework for BannkMint AI SMB Banking OS
Generates comprehensive financial reports for SMB management
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, extract
from collections import defaultdict, Counter
import calendar
from db import Transaction, Account

class MonthEndReportingService:
    """
    Month-End Reporting Framework for SMB financial management
    Generates executive summaries, P&L, cash flow statements
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_month_end_pack(self, 
                               month: Optional[int] = None, 
                               year: Optional[int] = None,
                               account_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive month-end reporting pack
        """
        # Default to previous month if not specified
        if month is None or year is None:
            today = datetime.now()
            if today.month == 1:
                month = 12
                year = today.year - 1
            else:
                month = today.month - 1
                year = today.year
        
        # Define reporting period
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # Generate all report components
        return {
            'report_period': {
                'month': month,
                'year': year,
                'month_name': calendar.month_name[month],
                'start_date': month_start.isoformat(),
                'end_date': month_end.isoformat()
            },
            'executive_summary': self._generate_executive_summary(month_start, month_end, account_ids),
            'profit_loss': self._generate_profit_loss(month_start, month_end, account_ids),
            'cash_flow_statement': self._generate_cash_flow_statement(month_start, month_end, account_ids),
            'balance_sheet_summary': self._generate_balance_sheet_summary(month_end, account_ids),
            'category_analysis': self._generate_category_analysis(month_start, month_end, account_ids),
            'vendor_analysis': self._generate_vendor_analysis(month_start, month_end, account_ids),
            'bank_account_summary': self._generate_bank_account_summary(month_end, account_ids),
            'key_metrics': self._generate_key_metrics(month_start, month_end, account_ids),
            'alerts_and_insights': self._generate_alerts_and_insights(month_start, month_end, account_ids),
            'generated_at': datetime.now().isoformat(),
            'report_type': 'month_end_pack'
        }
    
    def _generate_executive_summary(self, start_date: datetime, end_date: datetime, account_ids: Optional[List[str]]) -> Dict[str, Any]:
        """Generate executive summary for the reporting period"""
        
        # Get all transactions for the period
        query = self.db.query(Transaction).filter(
            and_(
                Transaction.posted_at >= start_date,
                Transaction.posted_at <= end_date
            )
        )
        
        if account_ids:
            query = query.filter(Transaction.account_id.in_(account_ids))
        
        transactions = query.all()
        
        if not transactions:
            return {
                'total_revenue': 0.0,
                'total_expenses': 0.0,
                'net_income': 0.0,
                'transaction_count': 0,
                'avg_transaction_size': 0.0,
                'revenue_categories': [],
                'expense_categories': [],
                'summary_text': "No transactions found for this period."
            }
        
        # Calculate summary metrics
        revenue_txns = [t for t in transactions if t.amount > 0]
        expense_txns = [t for t in transactions if t.amount < 0]
        
        total_revenue = sum(t.amount for t in revenue_txns)
        total_expenses = sum(abs(t.amount) for t in expense_txns)
        net_income = total_revenue - total_expenses
        
        # Top revenue and expense categories
        revenue_by_category = defaultdict(float)
        expense_by_category = defaultdict(float)
        
        for t in revenue_txns:
            revenue_by_category[t.category or 'Uncategorized'] += t.amount
        
        for t in expense_txns:
            expense_by_category[t.category or 'Uncategorized'] += abs(t.amount)
        
        # Sort categories by amount
        top_revenue_categories = sorted(revenue_by_category.items(), key=lambda x: x[1], reverse=True)[:5]
        top_expense_categories = sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Generate summary insights
        month_name = calendar.month_name[start_date.month]
        summary_text = self._generate_summary_text(total_revenue, total_expenses, net_income, month_name)
        
        return {
            'total_revenue': round(total_revenue, 2),
            'total_expenses': round(total_expenses, 2),
            'net_income': round(net_income, 2),
            'transaction_count': len(transactions),
            'avg_transaction_size': round(sum(abs(t.amount) for t in transactions) / len(transactions), 2),
            'revenue_categories': [{'category': cat, 'amount': round(amt, 2)} for cat, amt in top_revenue_categories],
            'expense_categories': [{'category': cat, 'amount': round(amt, 2)} for cat, amt in top_expense_categories],
            'summary_text': summary_text
        }
    
    def _generate_summary_text(self, revenue: float, expenses: float, net_income: float, month_name: str) -> str:
        """Generate executive summary text"""
        
        profit_margin = (net_income / revenue * 100) if revenue > 0 else 0
        
        summary = f"For {month_name}, the business generated ${revenue:,.2f} in revenue and incurred ${expenses:,.2f} in expenses, "
        
        if net_income > 0:
            summary += f"resulting in a net profit of ${net_income:,.2f} ({profit_margin:.1f}% profit margin)."
        else:
            summary += f"resulting in a net loss of ${abs(net_income):,.2f}."
        
        # Add context based on performance
        if profit_margin > 20:
            summary += " This represents strong profitability for the period."
        elif profit_margin > 10:
            summary += " This shows healthy business performance."
        elif profit_margin > 0:
            summary += " Profitability is positive but may benefit from expense optimization."
        else:
            summary += " Focus on revenue growth or expense reduction is recommended."
        
        return summary
    
    def _generate_profit_loss(self, start_date: datetime, end_date: datetime, account_ids: Optional[List[str]]) -> Dict[str, Any]:
        """Generate Profit & Loss statement"""
        
        query = self.db.query(Transaction).filter(
            and_(
                Transaction.posted_at >= start_date,
                Transaction.posted_at <= end_date
            )
        )
        
        if account_ids:
            query = query.filter(Transaction.account_id.in_(account_ids))
        
        transactions = query.all()
        
        # Categorize revenue and expenses
        revenue_items = defaultdict(float)
        expense_items = defaultdict(float)
        
        for t in transactions:
            category = t.category or 'Uncategorized'
            
            if t.amount > 0:
                revenue_items[category] += t.amount
            else:
                expense_items[category] += abs(t.amount)
        
        # Calculate totals
        total_revenue = sum(revenue_items.values())
        total_expenses = sum(expense_items.values())
        gross_profit = total_revenue
        operating_income = gross_profit - total_expenses
        
        # Format for P&L structure
        revenue_lines = [{'category': cat, 'amount': round(amt, 2)} for cat, amt in sorted(revenue_items.items(), key=lambda x: x[1], reverse=True)]
        expense_lines = [{'category': cat, 'amount': round(amt, 2)} for cat, amt in sorted(expense_items.items(), key=lambda x: x[1], reverse=True)]
        
        return {
            'revenue': {
                'line_items': revenue_lines,
                'total_revenue': round(total_revenue, 2)
            },
            'expenses': {
                'line_items': expense_lines,
                'total_expenses': round(total_expenses, 2)
            },
            'summary': {
                'gross_profit': round(gross_profit, 2),
                'operating_income': round(operating_income, 2),
                'profit_margin_pct': round((operating_income / total_revenue * 100) if total_revenue > 0 else 0, 2)
            }
        }
    
    def _generate_cash_flow_statement(self, start_date: datetime, end_date: datetime, account_ids: Optional[List[str]]) -> Dict[str, Any]:
        """Generate Cash Flow Statement"""
        
        # Get beginning and ending balances
        beginning_balance = self._get_balance_at_date(start_date - timedelta(days=1), account_ids)
        ending_balance = self._get_balance_at_date(end_date, account_ids)
        
        # Get transactions for the period
        query = self.db.query(Transaction).filter(
            and_(
                Transaction.posted_at >= start_date,
                Transaction.posted_at <= end_date
            )
        )
        
        if account_ids:
            query = query.filter(Transaction.account_id.in_(account_ids))
        
        transactions = query.all()
        
        # Categorize cash flows
        operating_cash_flows = []
        investing_cash_flows = []
        financing_cash_flows = []
        
        for t in transactions:
            category = t.category or 'Uncategorized'
            
            # Classify cash flow type based on category
            if category in ['Revenue', 'Sales', 'Services', 'Interest Income']:
                flow_type = 'operating'
            elif category in ['Equipment', 'Property', 'Investments']:
                flow_type = 'investing'
            elif category in ['Loan Payment', 'Line of Credit', 'Owner Investment']:
                flow_type = 'financing'
            else:
                flow_type = 'operating'  # Default to operating
            
            cash_flow_item = {
                'category': category,
                'amount': round(t.amount, 2),
                'description': t.description
            }
            
            if flow_type == 'operating':
                operating_cash_flows.append(cash_flow_item)
            elif flow_type == 'investing':
                investing_cash_flows.append(cash_flow_item)
            else:
                financing_cash_flows.append(cash_flow_item)
        
        # Calculate net cash flows
        net_operating = sum(item['amount'] for item in operating_cash_flows)
        net_investing = sum(item['amount'] for item in investing_cash_flows)
        net_financing = sum(item['amount'] for item in financing_cash_flows)
        
        net_change_in_cash = net_operating + net_investing + net_financing
        
        return {
            'beginning_cash': round(beginning_balance, 2),
            'operating_activities': {
                'items': operating_cash_flows,
                'net_operating_cash_flow': round(net_operating, 2)
            },
            'investing_activities': {
                'items': investing_cash_flows,
                'net_investing_cash_flow': round(net_investing, 2)
            },
            'financing_activities': {
                'items': financing_cash_flows,
                'net_financing_cash_flow': round(net_financing, 2)
            },
            'net_change_in_cash': round(net_change_in_cash, 2),
            'ending_cash': round(ending_balance, 2)
        }
    
    def _generate_balance_sheet_summary(self, as_of_date: datetime, account_ids: Optional[List[str]]) -> Dict[str, Any]:
        """Generate simplified balance sheet summary"""
        
        # Get current balances for all accounts
        accounts_query = self.db.query(Account)
        if account_ids:
            accounts_query = accounts_query.filter(Account.id.in_(account_ids))
        
        accounts = accounts_query.all()
        
        assets = []
        liabilities = []
        total_assets = 0.0
        total_liabilities = 0.0
        
        for account in accounts:
            # Get latest balance
            latest_txn = self.db.query(Transaction).filter(
                and_(
                    Transaction.account_id == account.id,
                    Transaction.posted_at <= as_of_date
                )
            ).order_by(desc(Transaction.posted_at)).first()
            
            balance = latest_txn.balance if latest_txn and latest_txn.balance else 0.0
            
            account_item = {
                'account_name': account.name,
                'account_type': self._classify_account_type(account.name),
                'balance': round(balance, 2)
            }
            
            if balance >= 0:
                assets.append(account_item)
                total_assets += balance
            else:
                liabilities.append({
                    **account_item,
                    'balance': round(abs(balance), 2)  # Show as positive for liability
                })
                total_liabilities += abs(balance)
        
        owner_equity = total_assets - total_liabilities
        
        return {
            'as_of_date': as_of_date.isoformat(),
            'assets': {
                'items': assets,
                'total_assets': round(total_assets, 2)
            },
            'liabilities': {
                'items': liabilities,
                'total_liabilities': round(total_liabilities, 2)
            },
            'equity': {
                'owner_equity': round(owner_equity, 2)
            },
            'balance_check': round(total_assets - total_liabilities - owner_equity, 2)  # Should be 0
        }
    
    def _generate_category_analysis(self, start_date: datetime, end_date: datetime, account_ids: Optional[List[str]]) -> Dict[str, Any]:
        """Generate detailed category analysis"""
        
        query = self.db.query(Transaction).filter(
            and_(
                Transaction.posted_at >= start_date,
                Transaction.posted_at <= end_date
            )
        )
        
        if account_ids:
            query = query.filter(Transaction.account_id.in_(account_ids))
        
        transactions = query.all()
        
        category_summary = defaultdict(lambda: {
            'total_amount': 0.0,
            'transaction_count': 0,
            'avg_amount': 0.0,
            'largest_transaction': 0.0,
            'is_revenue': False
        })
        
        for t in transactions:
            category = t.category or 'Uncategorized'
            amount = abs(t.amount)
            
            category_summary[category]['total_amount'] += amount
            category_summary[category]['transaction_count'] += 1
            category_summary[category]['largest_transaction'] = max(
                category_summary[category]['largest_transaction'], 
                amount
            )
            category_summary[category]['is_revenue'] = category_summary[category]['is_revenue'] or (t.amount > 0)
        
        # Calculate averages and format
        category_analysis = []
        for category, data in category_summary.items():
            data['avg_amount'] = data['total_amount'] / data['transaction_count']
            category_analysis.append({
                'category': category,
                'total_amount': round(data['total_amount'], 2),
                'transaction_count': data['transaction_count'],
                'avg_amount': round(data['avg_amount'], 2),
                'largest_transaction': round(data['largest_transaction'], 2),
                'is_revenue': data['is_revenue']
            })
        
        # Sort by total amount
        category_analysis.sort(key=lambda x: x['total_amount'], reverse=True)
        
        return {
            'categories': category_analysis,
            'total_categories': len(category_analysis),
            'top_expense_category': next((c for c in category_analysis if not c['is_revenue']), None),
            'top_revenue_category': next((c for c in category_analysis if c['is_revenue']), None)
        }
    
    def _generate_vendor_analysis(self, start_date: datetime, end_date: datetime, account_ids: Optional[List[str]]) -> Dict[str, Any]:
        """Generate vendor spending analysis"""
        
        query = self.db.query(Transaction).filter(
            and_(
                Transaction.posted_at >= start_date,
                Transaction.posted_at <= end_date,
                Transaction.vendor.isnot(None)
            )
        )
        
        if account_ids:
            query = query.filter(Transaction.account_id.in_(account_ids))
        
        transactions = query.all()
        
        vendor_summary = defaultdict(lambda: {
            'total_spent': 0.0,
            'transaction_count': 0,
            'avg_transaction': 0.0,
            'category': None
        })
        
        for t in transactions:
            vendor = t.vendor
            amount = abs(t.amount)
            
            vendor_summary[vendor]['total_spent'] += amount
            vendor_summary[vendor]['transaction_count'] += 1
            vendor_summary[vendor]['category'] = t.category  # Use latest category
        
        # Calculate averages and format
        vendor_analysis = []
        for vendor, data in vendor_summary.items():
            data['avg_transaction'] = data['total_spent'] / data['transaction_count']
            vendor_analysis.append({
                'vendor': vendor,
                'total_spent': round(data['total_spent'], 2),
                'transaction_count': data['transaction_count'],
                'avg_transaction': round(data['avg_transaction'], 2),
                'category': data['category']
            })
        
        # Sort by total spent
        vendor_analysis.sort(key=lambda x: x['total_spent'], reverse=True)
        
        return {
            'vendors': vendor_analysis[:20],  # Top 20 vendors
            'total_vendors': len(vendor_analysis),
            'top_vendor': vendor_analysis[0] if vendor_analysis else None
        }
    
    def _generate_bank_account_summary(self, as_of_date: datetime, account_ids: Optional[List[str]]) -> Dict[str, Any]:
        """Generate bank account balances summary"""
        
        accounts_query = self.db.query(Account)
        if account_ids:
            accounts_query = accounts_query.filter(Account.id.in_(account_ids))
        
        accounts = accounts_query.all()
        
        account_summaries = []
        total_balance = 0.0
        
        for account in accounts:
            # Get latest balance and transaction count
            latest_txn = self.db.query(Transaction).filter(
                and_(
                    Transaction.account_id == account.id,
                    Transaction.posted_at <= as_of_date
                )
            ).order_by(desc(Transaction.posted_at)).first()
            
            balance = latest_txn.balance if latest_txn and latest_txn.balance else 0.0
            
            # Count transactions for the month
            month_start = as_of_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_txn_count = self.db.query(Transaction).filter(
                and_(
                    Transaction.account_id == account.id,
                    Transaction.posted_at >= month_start,
                    Transaction.posted_at <= as_of_date
                )
            ).count()
            
            account_summaries.append({
                'account_id': account.id,
                'account_name': account.name,
                'institution': account.institution,
                'balance': round(balance, 2),
                'monthly_transactions': monthly_txn_count,
                'account_type': self._classify_account_type(account.name),
                'last_activity': latest_txn.posted_at.isoformat() if latest_txn else None
            })
            
            total_balance += balance
        
        return {
            'accounts': account_summaries,
            'total_balance': round(total_balance, 2),
            'account_count': len(account_summaries)
        }
    
    def _generate_key_metrics(self, start_date: datetime, end_date: datetime, account_ids: Optional[List[str]]) -> Dict[str, Any]:
        """Generate key business metrics"""
        
        # Get previous period for comparison
        period_length = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_length)
        prev_end = start_date - timedelta(days=1)
        
        # Current period metrics
        current_metrics = self._calculate_period_metrics(start_date, end_date, account_ids)
        
        # Previous period metrics
        previous_metrics = self._calculate_period_metrics(prev_start, prev_end, account_ids)
        
        # Calculate growth rates
        revenue_growth = self._calculate_growth_rate(
            previous_metrics['revenue'], 
            current_metrics['revenue']
        )
        
        expense_growth = self._calculate_growth_rate(
            previous_metrics['expenses'], 
            current_metrics['expenses']
        )
        
        return {
            'current_period': current_metrics,
            'previous_period': previous_metrics,
            'growth_metrics': {
                'revenue_growth_pct': revenue_growth,
                'expense_growth_pct': expense_growth,
                'profit_margin_current': round((current_metrics['net_income'] / current_metrics['revenue'] * 100) if current_metrics['revenue'] > 0 else 0, 2),
                'profit_margin_previous': round((previous_metrics['net_income'] / previous_metrics['revenue'] * 100) if previous_metrics['revenue'] > 0 else 0, 2)
            }
        }
    
    def _generate_alerts_and_insights(self, start_date: datetime, end_date: datetime, account_ids: Optional[List[str]]) -> List[Dict[str, Any]]:
        """Generate business alerts and insights"""
        
        alerts = []
        
        # Get current period metrics
        current_metrics = self._calculate_period_metrics(start_date, end_date, account_ids)
        
        # Low profit margin alert
        profit_margin = (current_metrics['net_income'] / current_metrics['revenue'] * 100) if current_metrics['revenue'] > 0 else 0
        if profit_margin < 10:
            alerts.append({
                'type': 'profit_margin_warning',
                'severity': 'medium' if profit_margin > 0 else 'high',
                'title': 'Low Profit Margin',
                'message': f'Profit margin of {profit_margin:.1f}% is below recommended 10% threshold',
                'recommendation': 'Consider reviewing expenses or increasing pricing'
            })
        
        # High expense categories
        query = self.db.query(Transaction).filter(
            and_(
                Transaction.posted_at >= start_date,
                Transaction.posted_at <= end_date,
                Transaction.amount < 0
            )
        )
        
        if account_ids:
            query = query.filter(Transaction.account_id.in_(account_ids))
        
        expense_txns = query.all()
        category_expenses = defaultdict(float)
        
        for t in expense_txns:
            category_expenses[t.category or 'Uncategorized'] += abs(t.amount)
        
        total_expenses = sum(category_expenses.values())
        
        for category, amount in category_expenses.items():
            if amount / total_expenses > 0.3:  # Category represents >30% of expenses
                alerts.append({
                    'type': 'high_expense_category',
                    'severity': 'medium',
                    'title': f'High {category} Expenses',
                    'message': f'{category} represents {amount/total_expenses*100:.1f}% of total expenses (${amount:,.2f})',
                    'recommendation': f'Review {category} spending for optimization opportunities'
                })
        
        # Add positive insights
        if profit_margin > 20:
            alerts.append({
                'type': 'positive_insight',
                'severity': 'low',
                'title': 'Strong Profitability',
                'message': f'Excellent profit margin of {profit_margin:.1f}%',
                'recommendation': 'Consider investing in growth opportunities'
            })
        
        return alerts
    
    # Helper methods
    def _get_balance_at_date(self, date: datetime, account_ids: Optional[List[str]]) -> float:
        """Get total balance across accounts at a specific date"""
        
        accounts_query = self.db.query(Account)
        if account_ids:
            accounts_query = accounts_query.filter(Account.id.in_(account_ids))
        
        accounts = accounts_query.all()
        total_balance = 0.0
        
        for account in accounts:
            latest_txn = self.db.query(Transaction).filter(
                and_(
                    Transaction.account_id == account.id,
                    Transaction.posted_at <= date
                )
            ).order_by(desc(Transaction.posted_at)).first()
            
            if latest_txn and latest_txn.balance:
                total_balance += latest_txn.balance
        
        return total_balance
    
    def _classify_account_type(self, account_name: str) -> str:
        """Classify account type from name"""
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
            return 'checking'
    
    def _calculate_period_metrics(self, start_date: datetime, end_date: datetime, account_ids: Optional[List[str]]) -> Dict[str, float]:
        """Calculate financial metrics for a period"""
        
        query = self.db.query(Transaction).filter(
            and_(
                Transaction.posted_at >= start_date,
                Transaction.posted_at <= end_date
            )
        )
        
        if account_ids:
            query = query.filter(Transaction.account_id.in_(account_ids))
        
        transactions = query.all()
        
        revenue = sum(t.amount for t in transactions if t.amount > 0)
        expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
        net_income = revenue - expenses
        
        return {
            'revenue': round(revenue, 2),
            'expenses': round(expenses, 2),
            'net_income': round(net_income, 2),
            'transaction_count': len(transactions)
        }
    
    def _calculate_growth_rate(self, old_value: float, new_value: float) -> float:
        """Calculate growth rate percentage"""
        if old_value == 0:
            return 0.0 if new_value == 0 else 100.0
        
        return round((new_value - old_value) / old_value * 100, 2)