"""
SMB-Focused Cash Flow Forecasting Service for BannkMint AI Banking OS
Phase 3B: Advanced forecasting with crisis alerts and scenario planning
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import statistics
from collections import defaultdict
import math
from db import execute_query

class ForecastingService:
    """Advanced cash flow forecasting tailored for SMB needs"""
    
    def __init__(self):
        self.forecast_periods = [4, 6, 8, 13]  # weeks
        self.confidence_threshold = 0.7
        self.crisis_threshold = 1000  # Alert if projected balance goes below this
        
    def generate_cash_flow_forecast(
        self, 
        weeks: int = 8, 
        scenario: str = "base",
        include_seasonal: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive cash flow forecast
        Scenarios: 'optimistic', 'base', 'pessimistic'
        """
        if weeks not in self.forecast_periods:
            weeks = 8  # Default to 8-week forecast
            
        # Get current balance
        current_balance = self._get_current_balance()
        
        # Analyze historical patterns
        historical_data = self._analyze_historical_patterns(weeks * 2)  # Use 2x weeks for analysis
        
        # Generate weekly projections
        projections = self._calculate_weekly_projections(
            weeks, historical_data, scenario, include_seasonal
        )
        
        # Detect crisis points
        crisis_alerts = self._detect_crisis_points(projections, current_balance)
        
        # Calculate key metrics
        metrics = self._calculate_forecast_metrics(projections, current_balance)
        
        # Generate recommendations
        recommendations = self._generate_forecast_recommendations(
            projections, crisis_alerts, metrics, scenario
        )
        
        return {
            "forecast_period": f"{weeks} weeks",
            "scenario": scenario,
            "current_balance": current_balance,
            "projections": projections,
            "key_metrics": metrics,
            "crisis_alerts": crisis_alerts,
            "recommendations": recommendations,
            "confidence_factors": historical_data.get("confidence_factors", {}),
            "seasonal_adjustments": include_seasonal,
            "generated_at": datetime.now().isoformat()
        }
    
    def _get_current_balance(self) -> float:
        """Get current total balance across all accounts"""
        try:
            accounts = execute_query("SELECT balance FROM accounts")
            return sum(float(acc['balance']) for acc in accounts)
        except:
            return 0.0
    
    def _analyze_historical_patterns(self, analysis_weeks: int) -> Dict[str, Any]:
        """Analyze historical transaction patterns for forecasting"""
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=analysis_weeks)
        
        # Get historical transactions
        transactions = execute_query(
            "SELECT * FROM transactions WHERE date >= ? ORDER BY date",
            (start_date.isoformat(),)
        )
        
        if not transactions:
            return {"weekly_patterns": {}, "confidence_factors": {}}
        
        # Group by week and category
        weekly_data = defaultdict(lambda: defaultdict(list))
        
        for trans in transactions:
            trans_date = datetime.fromisoformat(trans['date'].replace('Z', '+00:00'))
            week_key = trans_date.strftime("%Y-W%U")  # Year-Week format
            category = trans.get('category', 'Other')
            amount = float(trans['amount'])
            
            weekly_data[week_key][category].append(amount)
        
        # Calculate weekly patterns by category
        category_patterns = {}
        
        for week, categories in weekly_data.items():
            for category, amounts in categories.items():
                if category not in category_patterns:
                    category_patterns[category] = {
                        'weekly_totals': [],
                        'transaction_counts': [],
                        'avg_transaction_size': []
                    }
                
                weekly_total = sum(amounts)
                count = len(amounts)
                avg_size = weekly_total / count if count > 0 else 0
                
                category_patterns[category]['weekly_totals'].append(weekly_total)
                category_patterns[category]['transaction_counts'].append(count)
                category_patterns[category]['avg_transaction_size'].append(avg_size)
        
        # Calculate statistics for each category
        pattern_analysis = {}
        overall_confidence = 0.0
        
        for category, data in category_patterns.items():
            if len(data['weekly_totals']) >= 2:
                totals = data['weekly_totals']
                mean_total = statistics.mean(totals)
                std_dev = statistics.stdev(totals) if len(totals) > 1 else 0
                
                # Calculate trend
                trend = self._calculate_trend(totals)
                
                # Calculate confidence based on consistency
                coefficient_of_variation = (std_dev / abs(mean_total)) if mean_total != 0 else 1
                confidence = max(0.1, 1 - min(coefficient_of_variation, 0.9))
                
                pattern_analysis[category] = {
                    'mean_weekly': mean_total,
                    'std_dev': std_dev,
                    'trend': trend,
                    'confidence': confidence,
                    'sample_size': len(totals),
                    'avg_transaction_count': statistics.mean(data['transaction_counts']),
                    'avg_transaction_size': statistics.mean(data['avg_transaction_size'])
                }
                
                overall_confidence += confidence * abs(mean_total)
        
        # Normalize overall confidence
        total_volume = sum(abs(cat['mean_weekly']) for cat in pattern_analysis.values())
        overall_confidence = overall_confidence / total_volume if total_volume > 0 else 0.5
        
        return {
            "weekly_patterns": pattern_analysis,
            "confidence_factors": {
                "overall_confidence": overall_confidence,
                "data_quality": min(1.0, len(transactions) / 100),  # More transactions = better quality
                "pattern_stability": self._calculate_pattern_stability(category_patterns),
                "seasonal_detected": self._detect_seasonal_patterns(weekly_data)
            }
        }
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend using simple linear regression slope"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x_values = list(range(n))
        
        # Calculate slope using least squares
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _calculate_pattern_stability(self, category_patterns: Dict) -> float:
        """Calculate how stable the patterns are across categories"""
        if not category_patterns:
            return 0.5
        
        stability_scores = []
        
        for category, data in category_patterns.items():
            totals = data['weekly_totals']
            if len(totals) >= 3:
                # Calculate how much weekly values deviate from mean
                mean_val = statistics.mean(totals)
                if mean_val != 0:
                    deviations = [abs(val - mean_val) / abs(mean_val) for val in totals]
                    stability = 1 - min(1.0, statistics.mean(deviations))
                    stability_scores.append(stability)
        
        return statistics.mean(stability_scores) if stability_scores else 0.5
    
    def _detect_seasonal_patterns(self, weekly_data: Dict) -> bool:
        """Simple seasonal pattern detection"""
        # This is a simplified implementation
        # In production, would use more sophisticated time series analysis
        if len(weekly_data) < 8:  # Need at least 8 weeks of data
            return False
        
        # Check if there are recurring patterns in weekly totals
        weekly_totals = []
        sorted_weeks = sorted(weekly_data.keys())
        
        for week in sorted_weeks:
            week_total = sum(sum(amounts) for amounts in weekly_data[week].values())
            weekly_totals.append(week_total)
        
        # Simple check for cyclical patterns
        if len(weekly_totals) >= 4:
            # Check for 4-week cycles (monthly patterns)
            correlations = []
            for offset in [4, 8]:  # 4-week and 8-week cycles
                if len(weekly_totals) > offset:
                    correlation = self._calculate_correlation(
                        weekly_totals[:-offset], 
                        weekly_totals[offset:]
                    )
                    correlations.append(abs(correlation))
            
            return any(corr > 0.3 for corr in correlations)
        
        return False
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)
        
        denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
        
        if denominator == 0:
            return 0.0
        
        return (n * sum_xy - sum_x * sum_y) / denominator
    
    def _calculate_weekly_projections(
        self, 
        weeks: int, 
        historical_data: Dict, 
        scenario: str,
        include_seasonal: bool
    ) -> List[Dict[str, Any]]:
        """Calculate weekly cash flow projections"""
        projections = []
        patterns = historical_data.get("weekly_patterns", {})
        
        # Scenario multipliers
        scenario_multipliers = {
            "optimistic": {"revenue": 1.15, "expenses": 0.90},
            "base": {"revenue": 1.0, "expenses": 1.0},
            "pessimistic": {"revenue": 0.85, "expenses": 1.10}
        }
        
        multipliers = scenario_multipliers.get(scenario, scenario_multipliers["base"])
        
        for week in range(1, weeks + 1):
            week_projection = {
                "week": week,
                "date": (datetime.now() + timedelta(weeks=week)).strftime("%Y-%m-%d"),
                "projected_inflows": 0.0,
                "projected_outflows": 0.0,
                "net_flow": 0.0,
                "confidence": 0.0,
                "category_breakdown": {}
            }
            
            total_confidence_weight = 0.0
            weighted_confidence = 0.0
            
            for category, pattern in patterns.items():
                base_amount = pattern['mean_weekly']
                
                # Apply trend
                trend_adjustment = pattern['trend'] * week
                projected_amount = base_amount + trend_adjustment
                
                # Apply scenario multipliers
                if projected_amount > 0:  # Revenue
                    projected_amount *= multipliers["revenue"]
                else:  # Expenses
                    projected_amount *= multipliers["expenses"]
                
                # Apply seasonal adjustments (simplified)
                if include_seasonal and week % 4 == 0:  # Every 4th week
                    seasonal_factor = 1.1 if projected_amount > 0 else 0.9
                    projected_amount *= seasonal_factor
                
                week_projection["category_breakdown"][category] = {
                    "projected_amount": projected_amount,
                    "confidence": pattern['confidence']
                }
                
                # Aggregate flows
                if projected_amount > 0:
                    week_projection["projected_inflows"] += projected_amount
                else:
                    week_projection["projected_outflows"] += abs(projected_amount)
                
                # Weight confidence by transaction volume
                weight = abs(projected_amount)
                weighted_confidence += pattern['confidence'] * weight
                total_confidence_weight += weight
            
            week_projection["net_flow"] = (
                week_projection["projected_inflows"] - 
                week_projection["projected_outflows"]
            )
            
            week_projection["confidence"] = (
                weighted_confidence / total_confidence_weight 
                if total_confidence_weight > 0 else 0.5
            )
            
            projections.append(week_projection)
        
        return projections
    
    def _detect_crisis_points(
        self, 
        projections: List[Dict], 
        starting_balance: float
    ) -> List[Dict[str, Any]]:
        """Detect potential cash flow crisis points"""
        alerts = []
        running_balance = starting_balance
        
        for projection in projections:
            running_balance += projection["net_flow"]
            
            # Crisis detection
            if running_balance < self.crisis_threshold:
                severity = "critical" if running_balance < 0 else "high"
                
                alerts.append({
                    "week": projection["week"],
                    "date": projection["date"],
                    "projected_balance": running_balance,
                    "severity": severity,
                    "message": (
                        f"Cash flow crisis projected in Week {projection['week']}: "
                        f"Balance drops to ${running_balance:,.2f}"
                    ),
                    "confidence": projection["confidence"]
                })
            
            # Low balance warning
            elif running_balance < self.crisis_threshold * 5:  # 5x crisis threshold
                alerts.append({
                    "week": projection["week"],
                    "date": projection["date"],
                    "projected_balance": running_balance,
                    "severity": "medium",
                    "message": (
                        f"Low balance warning in Week {projection['week']}: "
                        f"Balance projected at ${running_balance:,.2f}"
                    ),
                    "confidence": projection["confidence"]
                })
            
            # Update balance for next iteration
            projection["projected_balance"] = running_balance
        
        return alerts
    
    def _calculate_forecast_metrics(
        self, 
        projections: List[Dict], 
        starting_balance: float
    ) -> Dict[str, Any]:
        """Calculate key forecast metrics"""
        if not projections:
            return {}
        
        total_inflows = sum(p["projected_inflows"] for p in projections)
        total_outflows = sum(p["projected_outflows"] for p in projections)
        net_flow = total_inflows - total_outflows
        
        # Calculate average weekly flows
        avg_weekly_inflow = total_inflows / len(projections)
        avg_weekly_outflow = total_outflows / len(projections)
        
        # Find minimum balance week
        min_balance = starting_balance
        min_balance_week = 0
        running_balance = starting_balance
        
        for projection in projections:
            running_balance += projection["net_flow"]
            if running_balance < min_balance:
                min_balance = running_balance
                min_balance_week = projection["week"]
        
        # Calculate cash runway (weeks until balance hits zero)
        cash_runway = None
        if avg_weekly_outflow > avg_weekly_inflow:  # Burning cash
            weekly_burn = avg_weekly_outflow - avg_weekly_inflow
            cash_runway = starting_balance / weekly_burn if weekly_burn > 0 else None
        
        # Overall forecast confidence
        overall_confidence = sum(p["confidence"] for p in projections) / len(projections)
        
        return {
            "total_projected_inflows": total_inflows,
            "total_projected_outflows": total_outflows,
            "net_cash_flow": net_flow,
            "avg_weekly_inflow": avg_weekly_inflow,
            "avg_weekly_outflow": avg_weekly_outflow,
            "weekly_burn_rate": avg_weekly_outflow - avg_weekly_inflow,
            "minimum_balance": min_balance,
            "minimum_balance_week": min_balance_week,
            "cash_runway_weeks": cash_runway,
            "ending_balance": projections[-1]["projected_balance"] if projections else starting_balance,
            "overall_confidence": overall_confidence
        }
    
    def _generate_forecast_recommendations(
        self,
        projections: List[Dict],
        crisis_alerts: List[Dict],
        metrics: Dict,
        scenario: str
    ) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on forecast"""
        recommendations = []
        
        # Crisis-based recommendations
        if crisis_alerts:
            critical_alerts = [a for a in crisis_alerts if a["severity"] == "critical"]
            if critical_alerts:
                earliest_crisis = min(critical_alerts, key=lambda x: x["week"])
                recommendations.append({
                    "type": "urgent",
                    "priority": "critical",
                    "title": "Immediate Cash Flow Action Required",
                    "description": (
                        f"Critical cash shortfall projected in Week {earliest_crisis['week']}. "
                        "Consider: accelerating receivables, securing emergency funding, "
                        "or implementing immediate cost reductions."
                    )
                })
        
        # Cash runway recommendations
        runway_weeks = metrics.get("cash_runway_weeks")
        if runway_weeks and runway_weeks < 12:  # Less than 3 months
            recommendations.append({
                "type": "planning",
                "priority": "high",
                "title": "Extend Cash Runway",
                "description": (
                    f"Current runway: {runway_weeks:.1f} weeks. Focus on extending "
                    "cash runway through revenue acceleration or expense optimization."
                )
            })
        
        # Scenario-specific recommendations
        if scenario == "pessimistic":
            recommendations.append({
                "type": "risk_management",
                "priority": "medium",
                "title": "Prepare for Downturn Scenario",
                "description": (
                    "Consider establishing contingency plans: identify critical vs. "
                    "non-critical expenses, explore flexible financing options."
                )
            })
        elif scenario == "optimistic":
            recommendations.append({
                "type": "growth",
                "priority": "medium",
                "title": "Capitalize on Growth Opportunities",
                "description": (
                    "Strong cash flow projected. Consider strategic investments "
                    "in growth initiatives or building cash reserves."
                )
            })
        
        # Weekly burn rate recommendations
        weekly_burn = metrics.get("weekly_burn_rate", 0)
        if weekly_burn > 0:  # Burning cash
            recommendations.append({
                "type": "efficiency",
                "priority": "medium",
                "title": "Optimize Weekly Cash Burn",
                "description": (
                    f"Weekly burn rate: ${weekly_burn:,.2f}. Analyze largest "
                    "expense categories for optimization opportunities."
                )
            })
        
        # Confidence-based recommendations
        overall_confidence = metrics.get("overall_confidence", 0)
        if overall_confidence < 0.6:
            recommendations.append({
                "type": "data_quality",
                "priority": "low",
                "title": "Improve Forecast Accuracy",
                "description": (
                    "Forecast confidence is low. Consider: more consistent transaction "
                    "categorization, regular data entry, or historical data cleanup."
                )
            })
        
        return recommendations[:5]  # Return top 5 recommendations

# Initialize service
forecasting_service = ForecastingService()

# For backward compatibility with server.py
SMBCashFlowForecaster = ForecastingService