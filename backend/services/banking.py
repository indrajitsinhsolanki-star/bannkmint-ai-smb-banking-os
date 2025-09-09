"""
Banking Integration Foundation for BannkMint AI SMB Banking OS
Phase 3A: Bank Connection Simulation & Executive Dashboard
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random
from db import execute_query, get_or_create_account, generate_id

class BankingService:
    """Banking integration and executive dashboard service"""
    
    def __init__(self):
        self.supported_banks = [
            "Chase Bank", "Bank of America", "Wells Fargo", 
            "Citibank", "Capital One", "US Bank", "PNC Bank",
            "TD Bank", "Regions Bank", "Fifth Third Bank"
        ]
    
    def simulate_bank_connection(self, bank_name: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """
        Simulate bank API connection for demo purposes
        In production, this would integrate with actual bank APIs (Plaid, Yodlee, etc.)
        """
        if bank_name not in self.supported_banks:
            return {
                "success": False,
                "error": f"Bank '{bank_name}' not supported",
                "supported_banks": self.supported_banks
            }
        
        # Simulate connection delay
        import time
        time.sleep(random.uniform(1, 3))
        
        # Simulate occasional connection failures (10% chance)
        if random.random() < 0.1:
            return {
                "success": False,
                "error": "Connection timeout - please try again",
                "retry_recommended": True
            }
        
        # Simulate successful connection
        account_id = get_or_create_account(f"{bank_name} Business Checking", "business_checking")
        
        return {
            "success": True,
            "bank_name": bank_name,
            "account_id": account_id,
            "account_type": "business_checking",
            "last_sync": datetime.now(),
            "available_features": [
                "transaction_sync",
                "balance_monitoring",
                "payment_initiation",
                "account_verification"
            ]
        }
    
    def get_executive_dashboard_data(self) -> Dict[str, Any]:
        """
        Generate executive dashboard summary
        Key metrics for SMB owners and executive decision making
        """
        # Get current balance across all accounts
        accounts = execute_query("SELECT * FROM accounts")
        total_balance = sum(float(acc.get('balance', 0)) for acc in accounts)
        
        # Get recent transactions (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_transactions = execute_query(
            "SELECT * FROM transactions WHERE date >= ? ORDER BY date DESC",
            (thirty_days_ago.isoformat(),)
        )
        
        # Calculate cash flow metrics
        total_inflows = sum(
            float(t['amount']) for t in recent_transactions 
            if float(t['amount']) > 0
        )
        total_outflows = abs(sum(
            float(t['amount']) for t in recent_transactions 
            if float(t['amount']) < 0
        ))
        net_cash_flow = total_inflows - total_outflows
        
        # Category analysis
        category_breakdown = {}
        for transaction in recent_transactions:
            category = transaction.get('category', 'Uncategorized')
            amount = float(transaction['amount'])
            if category not in category_breakdown:
                category_breakdown[category] = {'count': 0, 'total': 0}
            category_breakdown[category]['count'] += 1
            category_breakdown[category]['total'] += amount
        
        # Sort categories by absolute total amount
        sorted_categories = sorted(
            category_breakdown.items(),
            key=lambda x: abs(x[1]['total']),
            reverse=True
        )[:10]  # Top 10 categories
        
        # Cash burn rate (average daily outflow)
        if total_outflows > 0:
            daily_burn_rate = total_outflows / 30
            days_of_cash = total_balance / daily_burn_rate if daily_burn_rate > 0 else float('inf')
        else:
            daily_burn_rate = 0
            days_of_cash = float('inf')
        
        # Alert conditions
        alerts = []
        if total_balance < 10000:
            alerts.append({
                "type": "low_balance",
                "severity": "high",
                "message": f"Account balance below $10,000: ${total_balance:,.2f}"
            })
        
        if net_cash_flow < 0:
            alerts.append({
                "type": "negative_cash_flow",
                "severity": "medium",
                "message": f"Negative cash flow this month: -${abs(net_cash_flow):,.2f}"
            })
        
        if days_of_cash < 30 and days_of_cash != float('inf'):
            alerts.append({
                "type": "cash_runway",
                "severity": "high",
                "message": f"Only {days_of_cash:.0f} days of cash remaining at current burn rate"
            })
        
        return {
            "summary": {
                "total_balance": total_balance,
                "total_accounts": len(accounts),
                "net_cash_flow_30d": net_cash_flow,
                "total_transactions_30d": len(recent_transactions)
            },
            "cash_flow": {
                "inflows_30d": total_inflows,
                "outflows_30d": total_outflows,
                "net_flow_30d": net_cash_flow,
                "daily_burn_rate": daily_burn_rate,
                "days_of_cash": days_of_cash if days_of_cash != float('inf') else None
            },
            "top_categories": [
                {
                    "category": cat[0],
                    "transaction_count": cat[1]['count'],
                    "total_amount": cat[1]['total'],
                    "percentage": (abs(cat[1]['total']) / max(total_inflows + total_outflows, 1)) * 100
                }
                for cat in sorted_categories
            ],
            "alerts": alerts,
            "recommendations": self._generate_recommendations(
                total_balance, net_cash_flow, days_of_cash, category_breakdown
            ),
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_recommendations(
        self, 
        balance: float, 
        net_flow: float, 
        days_of_cash: float, 
        categories: Dict[str, Dict[str, float]]
    ) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on financial data"""
        recommendations = []
        
        # Balance-based recommendations
        if balance < 5000:
            recommendations.append({
                "type": "liquidity",
                "priority": "high",
                "title": "Critical: Improve Cash Position",
                "description": "Consider immediate cash flow measures: accelerate receivables, delay non-critical payments, or secure short-term financing."
            })
        elif balance < 25000:
            recommendations.append({
                "type": "liquidity",
                "priority": "medium",
                "title": "Build Cash Reserves",
                "description": "Aim for 3-6 months of operating expenses in cash reserves for financial stability."
            })
        
        # Cash flow recommendations
        if net_flow < -5000:
            recommendations.append({
                "type": "cash_flow",
                "priority": "high",
                "title": "Address Negative Cash Flow",
                "description": "Analyze largest expense categories and identify opportunities to reduce costs or increase revenue."
            })
        
        # Runway recommendations
        if days_of_cash < 60 and days_of_cash > 0:
            recommendations.append({
                "type": "planning",
                "priority": "high",
                "title": "Extend Cash Runway",
                "description": f"With {days_of_cash:.0f} days of cash remaining, prioritize revenue generation and expense optimization."
            })
        
        # Category-specific recommendations
        if categories:
            largest_expense = max(
                ((k, v) for k, v in categories.items() if v['total'] < 0),
                key=lambda x: abs(x[1]['total']),
                default=None
            )
            
            if largest_expense and abs(largest_expense[1]['total']) > 1000:
                recommendations.append({
                    "type": "optimization",
                    "priority": "medium",
                    "title": f"Optimize {largest_expense[0]} Spending",
                    "description": f"Your largest expense category ({largest_expense[0]}: ${abs(largest_expense[1]['total']):,.2f}) may have optimization opportunities."
                })
        
        return recommendations[:5]  # Limit to top 5 recommendations

# Initialize service instance
banking_service = BankingService()

# For backward compatibility with server.py
BankingIntegrationService = BankingService