"""
SMB-Focused Cash Flow Forecasting Service for BannkMint AI Banking OS
4-8 week actionable forecasts with crisis prevention and scenario planning
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from collections import defaultdict, Counter
import re
from db import Transaction, Account

class SMBCashFlowForecaster:
    """
    SMB-Focused Cash Flow Forecasting with crisis prevention
    Optimized for 4-8 week actionable business planning
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.crisis_threshold = 10000.0  # $10K cash flow crisis threshold
        self.default_weeks = 6  # SMB-optimal forecast period
        self.confidence_threshold = 0.7  # Higher confidence for SMB decisions
        
    def generate_smb_forecast(self, 
                             weeks: int = 6,
                             account_id: str = None,
                             scenario: str = "base") -> Dict:
        """
        Generate SMB-focused cash flow forecast with crisis prevention
        """
        # Validate weeks (4-8 week SMB focus)
        weeks = max(4, min(weeks, 8))
        
        # Get current financial position
        current_balances = self._get_current_balances(account_id)
        total_cash = sum(current_balances.values())
        
        # Detect SMB-specific recurring patterns
        patterns = self._detect_smb_patterns(account_id)
        
        # Generate daily projections with crisis detection
        projections = self._generate_daily_projections(
            weeks, patterns, total_cash, scenario
        )
        
        # Generate crisis alerts and recommendations
        alerts = self._generate_crisis_alerts(projections, patterns)
        
        # Calculate business metrics
        business_metrics = self._calculate_business_metrics(projections, patterns)
        
        # Generate scenario analysis
        scenario_analysis = self._generate_scenario_analysis(patterns, total_cash, weeks)
        
        return {
            'forecast_period': f"{weeks}_weeks",
            'scenario': scenario,
            'current_cash': round(total_cash, 2),
            'crisis_threshold': self.crisis_threshold,
            'daily_projections': projections,
            'smb_patterns': patterns,
            'crisis_alerts': alerts,
            'business_metrics': business_metrics,
            'scenario_analysis': scenario_analysis,
            'recommendations': self._generate_smb_recommendations(projections, patterns, alerts),
            'generated_at': datetime.now().isoformat()
        }
    
    def _detect_smb_patterns(self, account_id: str = None) -> List[Dict]:
        """
        Detect SMB-specific recurring patterns with high accuracy
        Focus on critical business payments: payroll, rent, subscriptions
        """
        # Get 4 months of data for better pattern detection
        cutoff_date = datetime.now() - timedelta(days=120)
        
        query = self.db.query(Transaction).filter(
            Transaction.posted_at >= cutoff_date
        )
        
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
            
        transactions = query.order_by(Transaction.posted_at.asc()).all()
        
        if len(transactions) < 8:
            return []
        
        # Group by SMB-specific vendor patterns
        smb_vendor_groups = defaultdict(list)
        
        for txn in transactions:
            vendor_key = self._normalize_smb_vendor(txn.vendor or txn.description, txn.category)
            if vendor_key:
                smb_vendor_groups[vendor_key].append({
                    'date': txn.posted_at,
                    'amount': txn.amount,
                    'description': txn.description,
                    'vendor': txn.vendor,
                    'category': txn.category
                })
        
        patterns = []
        for vendor, txn_list in smb_vendor_groups.items():
            if len(txn_list) >= 2:  # At least 2 occurrences
                pattern = self._analyze_smb_pattern(vendor, txn_list)
                if pattern and pattern['confidence'] >= self.confidence_threshold:
                    patterns.append(pattern)
        
        # Sort by business criticality and confidence
        patterns.sort(key=lambda x: (x['business_criticality'], x['confidence']), reverse=True)
        return patterns[:15]  # Top 15 most critical patterns
    
    def _normalize_smb_vendor(self, name: str, category: str) -> Optional[str]:
        """
        Normalize vendor names focusing on SMB-critical payments
        """
        if not name:
            return None
            
        name_lower = name.lower().strip()
        
        # SMB-critical vendor patterns
        critical_patterns = {
            # Payroll services (highest priority)
            'payroll': ['gusto', 'adp', 'paychex', 'quickbooks payroll', 'payroll', 'salary', 'wages'],
            
            # Rent & utilities (high priority)
            'rent': ['rent', 'lease', 'property management', 'landlord'],
            'utilities': ['electric', 'gas', 'water', 'internet', 'phone', 'telecom'],
            
            # Software subscriptions (medium priority)
            'saas': ['aws', 'microsoft', 'adobe', 'salesforce', 'zoom', 'slack', 'dropbox'],
            
            # Banking & financing (high priority)
            'loan': ['loan payment', 'line of credit', 'credit line', 'bank loan'],
            'credit_card': ['amex', 'visa', 'mastercard', 'credit card'],
            
            # Insurance (medium priority)
            'insurance': ['insurance', 'workers comp', 'liability', 'property insurance'],
            
            # Professional services (medium priority)  
            'professional': ['legal', 'accounting', 'cpa', 'lawyer', 'attorney', 'consultant']
        }
        
        # Match against critical patterns
        for pattern_type, keywords in critical_patterns.items():
            for keyword in keywords:
                if keyword in name_lower:
                    # Extract more specific vendor name
                    vendor_name = self._extract_vendor_name(name_lower, keyword)
                    return f"{pattern_type}_{vendor_name}"
        
        # Only include if it's a recognized business category
        if category and category in [
            'Payroll', 'Rent & Utilities', 'Software & Technology', 
            'Professional Services', 'Insurance', 'Banking Fees'
        ]:
            words = name_lower.split()[:2]
            return '_'.join(words) if words else None
        
        return None
    
    def _extract_vendor_name(self, description: str, keyword: str) -> str:
        """Extract specific vendor name from description"""
        # Remove common prefixes and transaction codes
        clean_desc = re.sub(r'[#*]\w+', '', description)
        clean_desc = re.sub(r'\b\d{4,}\b', '', clean_desc)
        
        words = clean_desc.split()
        vendor_words = [w for w in words if len(w) > 2 and w != keyword][:2]
        
        return '_'.join(vendor_words) if vendor_words else keyword
    
    def _analyze_smb_pattern(self, vendor: str, transactions: List[Dict]) -> Optional[Dict]:
        """
        Analyze SMB transaction patterns with business context
        """
        if len(transactions) < 2:
            return None
            
        transactions.sort(key=lambda x: x['date'])
        
        # Calculate intervals
        intervals = []
        for i in range(1, len(transactions)):
            delta = (transactions[i]['date'] - transactions[i-1]['date']).days
            intervals.append(delta)
        
        # SMB-specific pattern detection
        pattern_info = self._detect_smb_frequency(intervals)
        if not pattern_info:
            return None
        
        # Amount analysis
        amounts = [txn['amount'] for txn in transactions]
        avg_amount = np.mean(amounts)
        amount_std = np.std(amounts)
        
        # Business criticality scoring
        criticality = self._calculate_business_criticality(vendor, avg_amount, pattern_info['frequency'])
        
        # Confidence calculation (higher standards for SMBs)
        interval_consistency = self._calculate_interval_consistency(intervals, pattern_info['expected_interval'])
        amount_consistency = 1.0 - min(amount_std / abs(avg_amount), 0.5) if avg_amount != 0 else 0.5
        
        confidence = (interval_consistency * 0.8 + amount_consistency * 0.2)
        
        return {
            'vendor': vendor,
            'frequency': pattern_info['frequency'],
            'expected_interval': pattern_info['expected_interval'],
            'avg_amount': round(avg_amount, 2),
            'amount_std': round(amount_std, 2),
            'confidence': round(confidence, 3),
            'business_criticality': criticality,
            'occurrences': len(transactions),
            'last_occurrence': transactions[-1]['date'],
            'category': transactions[-1]['category'] or 'Uncategorized',
            'description': transactions[-1]['description'],
            'next_expected': self._calculate_next_expected_date(
                transactions[-1]['date'], 
                pattern_info['expected_interval']
            ),
            'cash_impact': 'negative' if avg_amount < 0 else 'positive'
        }
    
    def _detect_smb_frequency(self, intervals: List[int]) -> Optional[Dict]:
        """
        Detect SMB-relevant recurring patterns
        """
        if not intervals:
            return None
            
        # SMB-specific patterns (in days)
        smb_patterns = {
            'weekly': (7, 1),           # Weekly payments ± 1 day
            'bi_weekly': (14, 2),       # Bi-weekly payroll ± 2 days  
            'monthly': (30, 3),         # Monthly recurring ± 3 days
            'quarterly': (90, 7),       # Quarterly payments ± 1 week
        }
        
        for pattern_name, (expected_days, tolerance) in smb_patterns.items():
            matches = sum(1 for interval in intervals 
                         if abs(interval - expected_days) <= tolerance)
            
            if matches >= len(intervals) * 0.75:  # 75% consistency for SMBs
                return {
                    'frequency': pattern_name,
                    'expected_interval': expected_days,
                    'match_rate': matches / len(intervals)
                }
        
        return None
    
    def _calculate_business_criticality(self, vendor: str, amount: float, frequency: str) -> float:
        """
        Calculate business criticality score for SMB planning
        """
        base_criticality = 0.5
        
        # High criticality patterns
        if 'payroll' in vendor:
            base_criticality = 1.0  # Payroll is most critical
        elif 'rent' in vendor:
            base_criticality = 0.9  # Rent is second most critical
        elif 'loan' in vendor or 'credit' in vendor:
            base_criticality = 0.8  # Debt payments are critical
        elif 'utilities' in vendor:
            base_criticality = 0.7  # Utilities are important
        elif 'insurance' in vendor:
            base_criticality = 0.6  # Insurance is important
        elif 'saas' in vendor:
            base_criticality = 0.5  # Software subscriptions
        
        # Adjust for amount (larger amounts are more critical)
        amount_factor = min(abs(amount) / 5000, 1.0)  # Cap at $5K
        
        # Adjust for frequency (more frequent = more critical to predict)
        frequency_factor = {
            'weekly': 1.0,
            'bi_weekly': 0.9,
            'monthly': 0.8,
            'quarterly': 0.6
        }.get(frequency, 0.5)
        
        return round(base_criticality * (0.7 + 0.2 * amount_factor + 0.1 * frequency_factor), 2)
    
    def _calculate_interval_consistency(self, intervals: List[int], expected_interval: int) -> float:
        """Calculate how consistent the intervals are"""
        if not intervals:
            return 0.0
        
        deviations = [abs(interval - expected_interval) for interval in intervals]
        avg_deviation = np.mean(deviations)
        
        # Normalize deviation score (lower deviation = higher consistency)
        consistency = max(0.0, 1.0 - (avg_deviation / expected_interval))
        return consistency
    
    def _calculate_next_expected_date(self, last_date: datetime, interval_days: int) -> datetime:
        """Calculate the next expected transaction date"""
        return last_date + timedelta(days=interval_days)
    
    def _get_current_balances(self, account_id: str = None) -> Dict[str, float]:
        """Get current balances for all accounts"""
        balances = {}
        
        accounts_query = self.db.query(Account)
        if account_id:
            accounts_query = accounts_query.filter(Account.id == account_id)
        
        accounts = accounts_query.all()
        
        for account in accounts:
            # Get latest transaction with balance
            latest_txn = self.db.query(Transaction).filter(
                Transaction.account_id == account.id
            ).order_by(desc(Transaction.posted_at)).first()
            
            if latest_txn and latest_txn.balance is not None:
                balances[account.id] = latest_txn.balance
            else:
                balances[account.id] = 0.0
        
        return balances
    
    def _generate_daily_projections(self, 
                                   weeks: int, 
                                   patterns: List[Dict], 
                                   starting_cash: float,
                                   scenario: str) -> List[Dict]:
        """
        Generate daily cash flow projections with scenario adjustments
        """
        projections = []
        current_date = datetime.now().date()
        end_date = current_date + timedelta(weeks=weeks)
        running_cash = starting_cash
        
        # Scenario multipliers
        scenario_adjustments = {
            'optimistic': {'revenue': 1.15, 'expenses': 0.95},
            'base': {'revenue': 1.0, 'expenses': 1.0},
            'pessimistic': {'revenue': 0.85, 'expenses': 1.1}
        }
        
        adjustments = scenario_adjustments.get(scenario, scenario_adjustments['base'])
        
        while current_date <= end_date:
            daily_inflow = 0.0
            daily_outflow = 0.0
            expected_transactions = []
            
            # Check each pattern for expected transactions
            for pattern in patterns:
                if self._is_smb_transaction_due(current_date, pattern):
                    base_amount = pattern['avg_amount']
                    
                    # Apply scenario adjustments
                    if base_amount > 0:
                        adjusted_amount = base_amount * adjustments['revenue']
                    else:
                        adjusted_amount = base_amount * adjustments['expenses']
                    
                    # Add some realistic variance
                    if pattern['amount_std'] > 0:
                        variance = min(pattern['amount_std'] * 0.3, abs(adjusted_amount) * 0.1)
                        adjusted_amount += np.random.normal(0, variance)
                    
                    adjusted_amount = round(adjusted_amount, 2)
                    
                    if adjusted_amount > 0:
                        daily_inflow += adjusted_amount
                    else:
                        daily_outflow += abs(adjusted_amount)
                    
                    expected_transactions.append({
                        'vendor': pattern['vendor'],
                        'amount': adjusted_amount,
                        'confidence': pattern['confidence'],
                        'criticality': pattern['business_criticality']
                    })
            
            # Update running cash
            net_flow = daily_inflow - daily_outflow
            running_cash += net_flow
            
            # Check for crisis threshold
            crisis_warning = running_cash < self.crisis_threshold
            
            projections.append({
                'date': current_date.isoformat(),
                'cash_balance': round(running_cash, 2),
                'daily_inflow': round(daily_inflow, 2),
                'daily_outflow': round(daily_outflow, 2),
                'net_flow': round(net_flow, 2),
                'crisis_warning': crisis_warning,
                'expected_transactions': expected_transactions,
                'days_from_today': (current_date - datetime.now().date()).days
            })
            
            current_date += timedelta(days=1)
        
        return projections
    
    def _is_smb_transaction_due(self, date: datetime.date, pattern: Dict) -> bool:
        """
        Determine if an SMB transaction is due on a specific date
        """
        next_expected = pattern['next_expected'].date()
        interval = pattern['expected_interval']
        
        # Tighter tolerance for SMB predictions
        tolerance = max(interval * 0.08, 1)  # 8% tolerance, minimum 1 day
        
        date_diff = abs((date - next_expected).days)
        
        if date_diff <= tolerance:
            return True
        
        # Check future occurrences
        days_since_expected = (date - next_expected).days
        if days_since_expected > 0:
            cycles_passed = days_since_expected / interval
            if abs(cycles_passed - round(cycles_passed)) * interval <= tolerance:
                return True
        
        return False
    
    def _generate_crisis_alerts(self, projections: List[Dict], patterns: List[Dict]) -> List[Dict]:
        """
        Generate SMB-specific cash flow crisis alerts
        """
        alerts = []
        
        # Crisis threshold alerts
        crisis_days = [p for p in projections if p['crisis_warning']]
        
        if crisis_days:
            first_crisis = crisis_days[0]
            days_to_crisis = first_crisis['days_from_today']
            
            severity = 'critical' if days_to_crisis <= 7 else 'high' if days_to_crisis <= 14 else 'medium'
            
            alerts.append({
                'type': 'cash_flow_crisis',
                'severity': severity,
                'title': f'Cash Flow Crisis Alert',
                'message': f'Balance will drop below ${self.crisis_threshold:,.0f} in {days_to_crisis} days',
                'date': first_crisis['date'],
                'projected_balance': first_crisis['cash_balance'],
                'recommendations': self._get_crisis_recommendations(first_crisis, patterns)
            })
        
        # Large payment alerts
        large_payments = []
        for projection in projections[:14]:  # Next 2 weeks
            for txn in projection['expected_transactions']:
                if txn['amount'] < -5000:  # Large outflows
                    large_payments.append({
                        'date': projection['date'],
                        'vendor': txn['vendor'],
                        'amount': txn['amount'],
                        'criticality': txn['criticality']
                    })
        
        if large_payments:
            alerts.append({
                'type': 'large_payments_ahead',
                'severity': 'medium',
                'title': 'Large Payments Coming',
                'message': f'{len(large_payments)} large payments totaling ${sum(p["amount"] for p in large_payments):,.0f}',
                'payments': large_payments[:5]  # Top 5
            })
        
        return alerts
    
    def _get_crisis_recommendations(self, crisis_projection: Dict, patterns: List[Dict]) -> List[str]:
        """
        Generate actionable recommendations for cash flow crisis
        """
        recommendations = []
        
        # Identify deferrable expenses
        deferrable = [p for p in patterns if p['business_criticality'] < 0.7 and p['avg_amount'] < 0]
        if deferrable:
            total_deferrable = sum(abs(p['avg_amount']) for p in deferrable[:3])
            recommendations.append(f"Consider deferring ${total_deferrable:,.0f} in non-critical expenses")
        
        # Line of credit recommendation
        shortage = abs(crisis_projection['cash_balance'])
        recommendations.append(f"Ensure ${shortage * 1.5:,.0f} line of credit is available")
        
        # Accelerate receivables
        recommendations.append("Contact clients to accelerate outstanding invoice payments")
        
        # Inventory management
        recommendations.append("Review inventory levels for potential cash conversion")
        
        return recommendations
    
    def _calculate_business_metrics(self, projections: List[Dict], patterns: List[Dict]) -> Dict:
        """
        Calculate SMB-relevant business metrics
        """
        if not projections:
            return {}
        
        # Cash runway calculation
        current_cash = projections[0]['cash_balance']
        avg_daily_burn = np.mean([abs(p['net_flow']) for p in projections if p['net_flow'] < 0])
        cash_runway_days = current_cash / avg_daily_burn if avg_daily_burn > 0 else 999
        
        # Recurring revenue/expenses
        recurring_inflows = sum(p['avg_amount'] for p in patterns if p['avg_amount'] > 0)
        recurring_outflows = sum(abs(p['avg_amount']) for p in patterns if p['avg_amount'] < 0)
        
        # Forecast accuracy indicators
        high_confidence_patterns = len([p for p in patterns if p['confidence'] > 0.8])
        
        return {
            'cash_runway_days': round(cash_runway_days, 1),
            'cash_runway_weeks': round(cash_runway_days / 7, 1),
            'monthly_recurring_revenue': round(recurring_inflows * 4.33, 2),  # Weekly to monthly
            'monthly_recurring_expenses': round(recurring_outflows * 4.33, 2),
            'net_monthly_recurring': round((recurring_inflows - recurring_outflows) * 4.33, 2),
            'forecast_confidence': round(high_confidence_patterns / len(patterns) if patterns else 0, 2),
            'total_patterns_detected': len(patterns),
            'critical_patterns': len([p for p in patterns if p['business_criticality'] > 0.8])
        }
    
    def _generate_scenario_analysis(self, patterns: List[Dict], current_cash: float, weeks: int) -> Dict:
        """
        Generate scenario planning analysis for business decisions
        """
        scenarios = {}
        
        for scenario_name in ['optimistic', 'base', 'pessimistic']:
            scenario_projections = self._generate_daily_projections(
                weeks, patterns, current_cash, scenario_name
            )
            
            ending_cash = scenario_projections[-1]['cash_balance']
            min_cash = min(p['cash_balance'] for p in scenario_projections)
            crisis_days = len([p for p in scenario_projections if p['crisis_warning']])
            
            scenarios[scenario_name] = {
                'ending_cash': round(ending_cash, 2),
                'minimum_cash': round(min_cash, 2),
                'crisis_days': crisis_days,
                'cash_change': round(ending_cash - current_cash, 2)
            }
        
        return scenarios
    
    def _generate_smb_recommendations(self, projections: List[Dict], patterns: List[Dict], alerts: List[Dict]) -> List[Dict]:
        """
        Generate actionable SMB recommendations
        """
        recommendations = []
        
        # Cash flow optimization
        if any(alert['severity'] in ['critical', 'high'] for alert in alerts):
            recommendations.append({
                'category': 'Cash Flow Management',
                'priority': 'high',
                'title': 'Immediate Cash Flow Action Required',
                'actions': [
                    'Review all upcoming large payments for deferral options',
                    'Accelerate collection of outstanding invoices',
                    'Consider short-term financing options'
                ]
            })
        
        # Pattern optimization  
        low_confidence_patterns = [p for p in patterns if p['confidence'] < 0.7]
        if low_confidence_patterns:
            recommendations.append({
                'category': 'Forecast Accuracy',
                'priority': 'medium',
                'title': 'Improve Payment Predictability',
                'actions': [
                    'Set up automatic payments for regular expenses',
                    'Negotiate fixed payment dates with vendors',
                    'Review irregular payment patterns'
                ]
            })
        
        # Growth planning
        if not any(alert['severity'] == 'critical' for alert in alerts):
            positive_cash_flow = sum(p['net_flow'] for p in projections if p['net_flow'] > 0)
            if positive_cash_flow > 0:
                recommendations.append({
                    'category': 'Growth Planning',
                    'priority': 'low',
                    'title': 'Cash Available for Investment',
                    'actions': [
                        f'Projected ${positive_cash_flow:,.0f} excess cash available',
                        'Consider strategic investments or expansion opportunities',
                        'Build emergency cash reserves to 3-6 months expenses'
                    ]
                })
        
        return recommendations