"""
Month-End Reporting Framework for BannkMint AI SMB Banking OS
Phase 3A: Executive reporting and month-end packages
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import calendar
from collections import defaultdict
from db import execute_query

class ReportingService:
    """Month-end reporting and executive dashboard service"""
    
    def __init__(self):
        self.report_categories = [
            'Revenue - Sales', 'Revenue - Services', 'Revenue - Other',
            'Office Expenses', 'Software & Technology', 'Marketing & Advertising',
            'Professional Services', 'Utilities', 'Rent & Facilities',
            'Insurance', 'Travel & Transportation', 'Meals & Entertainment',
            'Equipment & Supplies', 'Banking & Fees', 'Taxes',
            'Payroll & Benefits', 'Loan Payments'
        ]
    
    def generate_month_end_report(
        self, 
        year: int = None, 
        month: int = None,
        include_comparisons: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive month-end financial report
        """
        # Default to current month if not specified
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        # Calculate date ranges
        report_start = datetime(year, month, 1)
        report_end = datetime(year, month, calendar.monthrange(year, month)[1])
        
        # Previous month for comparison
        prev_start, prev_end = self._get_previous_month_range(year, month)
        
        # Get transaction data
        current_transactions = self._get_transactions_for_period(report_start, report_end)
        
        # Generate report sections
        income_statement = self._generate_income_statement(current_transactions)
        cash_flow_statement = self._generate_cash_flow_summary(current_transactions)
        category_analysis = self._generate_category_analysis(current_transactions)
        
        # Comparison data if requested
        comparisons = {}
        if include_comparisons and prev_start and prev_end:
            prev_transactions = self._get_transactions_for_period(prev_start, prev_end)
            comparisons = self._generate_period_comparisons(
                current_transactions, prev_transactions
            )
        
        # Key metrics and alerts
        key_metrics = self._calculate_key_metrics(current_transactions)
        alerts = self._generate_month_end_alerts(current_transactions, key_metrics)
        
        # Executive summary
        executive_summary = self._generate_executive_summary(
            income_statement, cash_flow_statement, key_metrics, alerts
        )
        
        return {
            "report_period": {
                "year": year,
                "month": month,
                "month_name": calendar.month_name[month],
                "start_date": report_start.date().isoformat(),
                "end_date": report_end.date().isoformat()
            },
            "executive_summary": executive_summary,
            "income_statement": income_statement,
            "cash_flow_summary": cash_flow_statement,
            "category_analysis": category_analysis,
            "key_metrics": key_metrics,
            "period_comparisons": comparisons,
            "alerts_and_insights": alerts,
            "generated_at": datetime.now().isoformat(),
            "report_type": "month_end_package"
        }
    
    def _get_transactions_for_period(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get all transactions for a specific period"""
        try:
            transactions = execute_query(
                """SELECT t.*, a.name as account_name 
                   FROM transactions t 
                   JOIN accounts a ON t.account_id = a.id 
                   WHERE t.date >= ? AND t.date <= ? 
                   ORDER BY t.date""",
                (start_date.isoformat(), end_date.isoformat())
            )
            
            # Convert to proper types
            for trans in transactions:
                trans['amount'] = float(trans['amount'])
                trans['confidence'] = float(trans.get('confidence', 0))
                
            return transactions
            
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return []
    
    def _generate_income_statement(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Generate income statement from transactions"""
        revenue_categories = ['Revenue - Sales', 'Revenue - Services', 'Revenue - Other']
        
        # Categorize transactions
        revenue_items = []
        expense_items = []
        
        for trans in transactions:
            category = trans.get('category', 'Uncategorized')
            amount = trans['amount']
            
            if amount > 0:  # Revenue
                revenue_items.append({
                    "category": category,
                    "amount": amount,
                    "transaction_count": 1
                })
            else:  # Expense
                expense_items.append({
                    "category": category,
                    "amount": abs(amount),
                    "transaction_count": 1
                })
        
        # Aggregate by category
        revenue_by_category = defaultdict(lambda: {"amount": 0, "count": 0})
        expense_by_category = defaultdict(lambda: {"amount": 0, "count": 0})
        
        for item in revenue_items:
            category = item["category"]
            revenue_by_category[category]["amount"] += item["amount"]
            revenue_by_category[category]["count"] += 1
        
        for item in expense_items:
            category = item["category"]
            expense_by_category[category]["amount"] += item["amount"]
            expense_by_category[category]["count"] += 1
        
        # Calculate totals
        total_revenue = sum(cat["amount"] for cat in revenue_by_category.values())
        total_expenses = sum(cat["amount"] for cat in expense_by_category.values())
        net_income = total_revenue - total_expenses
        
        # Format for output
        revenue_breakdown = [
            {
                "category": cat,
                "amount": data["amount"],
                "transaction_count": data["count"],
                "percentage_of_revenue": (data["amount"] / total_revenue * 100) if total_revenue > 0 else 0
            }
            for cat, data in sorted(revenue_by_category.items(), key=lambda x: x[1]["amount"], reverse=True)
        ]
        
        expense_breakdown = [
            {
                "category": cat,
                "amount": data["amount"],
                "transaction_count": data["count"],
                "percentage_of_expenses": (data["amount"] / total_expenses * 100) if total_expenses > 0 else 0
            }
            for cat, data in sorted(expense_by_category.items(), key=lambda x: x[1]["amount"], reverse=True)
        ]
        
        return {
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_income": net_income,
            "gross_margin": (total_revenue - total_expenses) / total_revenue * 100 if total_revenue > 0 else 0,
            "revenue_breakdown": revenue_breakdown,
            "expense_breakdown": expense_breakdown
        }
    
    def _generate_cash_flow_summary(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Generate cash flow summary"""
        total_inflows = sum(trans['amount'] for trans in transactions if trans['amount'] > 0)
        total_outflows = abs(sum(trans['amount'] for trans in transactions if trans['amount'] < 0))
        net_cash_flow = total_inflows - total_outflows
        
        # Daily cash flow analysis
        daily_flows = defaultdict(lambda: {"inflows": 0, "outflows": 0})
        
        for trans in transactions:
            date_key = trans['date'][:10]  # Extract date part
            amount = trans['amount']
            
            if amount > 0:
                daily_flows[date_key]["inflows"] += amount
            else:
                daily_flows[date_key]["outflows"] += abs(amount)
        
        # Calculate average daily flows
        days_with_activity = len(daily_flows)
        avg_daily_inflow = total_inflows / days_with_activity if days_with_activity > 0 else 0
        avg_daily_outflow = total_outflows / days_with_activity if days_with_activity > 0 else 0
        
        # Find peak days
        max_inflow_day = max(daily_flows.items(), key=lambda x: x[1]["inflows"], default=(None, {"inflows": 0}))
        max_outflow_day = max(daily_flows.items(), key=lambda x: x[1]["outflows"], default=(None, {"outflows": 0}))
        
        return {
            "total_cash_inflows": total_inflows,
            "total_cash_outflows": total_outflows,
            "net_cash_flow": net_cash_flow,
            "average_daily_inflow": avg_daily_inflow,
            "average_daily_outflow": avg_daily_outflow,
            "days_with_activity": days_with_activity,
            "peak_inflow_day": {
                "date": max_inflow_day[0],
                "amount": max_inflow_day[1]["inflows"]
            },
            "peak_outflow_day": {
                "date": max_outflow_day[0],
                "amount": max_outflow_day[1]["outflows"]
            }
        }
    
    def _generate_category_analysis(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Detailed category analysis"""
        category_stats = defaultdict(lambda: {
            "total_amount": 0,
            "transaction_count": 0,
            "avg_transaction_size": 0,
            "confidence_scores": []
        })
        
        for trans in transactions:
            category = trans.get('category', 'Uncategorized')
            amount = abs(trans['amount'])  # Use absolute value for analysis
            confidence = trans.get('confidence', 0)
            
            category_stats[category]["total_amount"] += amount
            category_stats[category]["transaction_count"] += 1
            category_stats[category]["confidence_scores"].append(confidence)
        
        # Calculate averages and format output
        category_analysis = []
        total_volume = sum(stats["total_amount"] for stats in category_stats.values())
        
        for category, stats in category_stats.items():
            avg_confidence = (
                sum(stats["confidence_scores"]) / len(stats["confidence_scores"])
                if stats["confidence_scores"] else 0
            )
            
            category_analysis.append({
                "category": category,
                "total_amount": stats["total_amount"],
                "transaction_count": stats["transaction_count"],
                "average_transaction_size": stats["total_amount"] / stats["transaction_count"],
                "percentage_of_total": (stats["total_amount"] / total_volume * 100) if total_volume > 0 else 0,
                "average_confidence": avg_confidence,
                "data_quality": "high" if avg_confidence > 0.8 else "medium" if avg_confidence > 0.5 else "low"
            })
        
        # Sort by total amount
        category_analysis.sort(key=lambda x: x["total_amount"], reverse=True)
        
        return {
            "categories": category_analysis,
            "total_categories": len(category_analysis),
            "uncategorized_percentage": next(
                (cat["percentage_of_total"] for cat in category_analysis if cat["category"] == "Uncategorized"),
                0
            )
        }
    
    def _calculate_key_metrics(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Calculate key financial metrics"""
        if not transactions:
            return {}
        
        # Basic calculations
        total_revenue = sum(trans['amount'] for trans in transactions if trans['amount'] > 0)
        total_expenses = abs(sum(trans['amount'] for trans in transactions if trans['amount'] < 0))
        transaction_count = len(transactions)
        
        # Average transaction sizes
        revenue_transactions = [trans['amount'] for trans in transactions if trans['amount'] > 0]
        expense_transactions = [abs(trans['amount']) for trans in transactions if trans['amount'] < 0]
        
        avg_revenue_per_transaction = sum(revenue_transactions) / len(revenue_transactions) if revenue_transactions else 0
        avg_expense_per_transaction = sum(expense_transactions) / len(expense_transactions) if expense_transactions else 0
        
        # Daily metrics
        date_range = []
        for trans in transactions:
            date_str = trans['date'][:10]
            if date_str not in date_range:
                date_range.append(date_str)
        
        active_days = len(date_range)
        avg_daily_transactions = transaction_count / active_days if active_days > 0 else 0
        
        # Cash efficiency metrics
        cash_conversion_ratio = total_revenue / total_expenses if total_expenses > 0 else float('inf')
        
        return {
            "total_transaction_volume": total_revenue + total_expenses,
            "revenue_to_expense_ratio": cash_conversion_ratio,
            "average_revenue_per_transaction": avg_revenue_per_transaction,
            "average_expense_per_transaction": avg_expense_per_transaction,
            "active_business_days": active_days,
            "average_daily_transactions": avg_daily_transactions,
            "largest_single_revenue": max(revenue_transactions) if revenue_transactions else 0,
            "largest_single_expense": max(expense_transactions) if expense_transactions else 0
        }
    
    def _get_previous_month_range(self, year: int, month: int) -> tuple:
        """Get date range for previous month"""
        try:
            if month == 1:
                prev_year, prev_month = year - 1, 12
            else:
                prev_year, prev_month = year, month - 1
            
            prev_start = datetime(prev_year, prev_month, 1)
            prev_end = datetime(prev_year, prev_month, calendar.monthrange(prev_year, prev_month)[1])
            
            return prev_start, prev_end
        except:
            return None, None
    
    def _generate_period_comparisons(
        self, 
        current_transactions: List[Dict], 
        previous_transactions: List[Dict]
    ) -> Dict[str, Any]:
        """Generate month-over-month comparisons"""
        # Current period metrics
        current_revenue = sum(t['amount'] for t in current_transactions if t['amount'] > 0)
        current_expenses = abs(sum(t['amount'] for t in current_transactions if t['amount'] < 0))
        current_net = current_revenue - current_expenses
        
        # Previous period metrics
        prev_revenue = sum(t['amount'] for t in previous_transactions if t['amount'] > 0)
        prev_expenses = abs(sum(t['amount'] for t in previous_transactions if t['amount'] < 0))
        prev_net = prev_revenue - prev_expenses
        
        # Calculate changes
        def calculate_change(current, previous):
            if previous == 0:
                return float('inf') if current > 0 else 0
            return ((current - previous) / previous) * 100
        
        return {
            "revenue_change": {
                "amount_change": current_revenue - prev_revenue,
                "percentage_change": calculate_change(current_revenue, prev_revenue)
            },
            "expense_change": {
                "amount_change": current_expenses - prev_expenses,
                "percentage_change": calculate_change(current_expenses, prev_expenses)
            },
            "net_income_change": {
                "amount_change": current_net - prev_net,
                "percentage_change": calculate_change(current_net, prev_net)
            },
            "transaction_count_change": {
                "amount_change": len(current_transactions) - len(previous_transactions),
                "percentage_change": calculate_change(len(current_transactions), len(previous_transactions))
            }
        }
    
    def _generate_month_end_alerts(
        self, 
        transactions: List[Dict], 
        metrics: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate month-end alerts and insights"""
        alerts = []
        
        # Revenue analysis
        total_revenue = sum(trans['amount'] for trans in transactions if trans['amount'] > 0)
        if total_revenue < 10000:
            alerts.append({
                "type": "revenue",
                "severity": "medium",
                "title": "Low Revenue Month",
                "message": f"Monthly revenue of ${total_revenue:,.2f} is below typical SMB benchmarks"
            })
        
        # Expense analysis
        total_expenses = abs(sum(trans['amount'] for trans in transactions if trans['amount'] < 0))
        if total_expenses > total_revenue * 1.2:  # Expenses > 120% of revenue
            alerts.append({
                "type": "expenses",
                "severity": "high",
                "title": "High Expense Ratio",
                "message": f"Expenses (${total_expenses:,.2f}) exceed revenue by {((total_expenses/total_revenue-1)*100):.1f}%"
            })
        
        # Data quality analysis
        uncategorized_count = len([t for t in transactions if not t.get('category') or t.get('category') == 'Uncategorized'])
        if uncategorized_count > len(transactions) * 0.2:  # >20% uncategorized
            alerts.append({
                "type": "data_quality",
                "severity": "low",
                "title": "Categorization Needed",
                "message": f"{uncategorized_count} transactions need categorization for better insights"
            })
        
        # Transaction volume analysis
        if len(transactions) < 20:  # Very few transactions
            alerts.append({
                "type": "activity",
                "severity": "medium",
                "title": "Low Transaction Volume",
                "message": f"Only {len(transactions)} transactions this month - consider business activity review"
            })
        
        return alerts
    
    def _generate_executive_summary(
        self,
        income_statement: Dict,
        cash_flow: Dict,
        metrics: Dict,
        alerts: List[Dict]
    ) -> Dict[str, Any]:
        """Generate executive summary with key insights"""
        # Determine overall financial health
        net_income = income_statement.get('net_income', 0)
        revenue = income_statement.get('total_revenue', 0)
        
        if net_income > 0:
            financial_health = "positive"
            health_message = f"Profitable month with ${net_income:,.2f} net income"
        elif net_income > -revenue * 0.1:  # Loss < 10% of revenue
            financial_health = "stable"
            health_message = f"Minor loss of ${abs(net_income):,.2f}, within acceptable range"
        else:
            financial_health = "concerning"
            health_message = f"Significant loss of ${abs(net_income):,.2f} requires attention"
        
        # Key highlights
        highlights = []
        
        if revenue > 0:
            highlights.append(f"Generated ${revenue:,.2f} in revenue")
        
        if cash_flow.get('net_cash_flow', 0) > 0:
            highlights.append(f"Positive cash flow of ${cash_flow['net_cash_flow']:,.2f}")
        
        expense_ratio = (income_statement.get('total_expenses', 0) / revenue * 100) if revenue > 0 else 0
        if expense_ratio < 80:
            highlights.append(f"Healthy expense ratio of {expense_ratio:.1f}%")
        
        # Critical issues
        critical_issues = [alert['message'] for alert in alerts if alert['severity'] == 'high']
        
        return {
            "financial_health": financial_health,
            "health_message": health_message,
            "key_highlights": highlights,
            "critical_issues": critical_issues,
            "total_alerts": len(alerts),
            "recommended_actions": self._generate_recommended_actions(income_statement, alerts)
        }
    
    def _generate_recommended_actions(self, income_statement: Dict, alerts: List[Dict]) -> List[str]:
        """Generate recommended actions based on analysis"""
        actions = []
        
        # Based on financial performance
        net_income = income_statement.get('net_income', 0)
        if net_income < 0:
            actions.append("Review and optimize largest expense categories")
            actions.append("Explore opportunities to increase revenue streams")
        
        # Based on alerts
        high_priority_alerts = [a for a in alerts if a['severity'] == 'high']
        if high_priority_alerts:
            actions.append("Address high-priority financial alerts immediately")
        
        # General recommendations
        if len(actions) == 0:
            actions.append("Continue monitoring cash flow trends")
            actions.append("Consider strategic investments for growth")
        
        return actions[:5]  # Limit to 5 recommendations

# Initialize service
reporting_service = ReportingService()

# For backward compatibility with server.py  
MonthEndReportingService = ReportingService