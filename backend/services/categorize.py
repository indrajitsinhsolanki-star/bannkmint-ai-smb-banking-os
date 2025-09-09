"""
AI categorization service for BannkMint AI
Enhanced categorization with learning from corrections
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from db import execute_query, generate_id

class CategorizationService:
    """Enhanced transaction categorization with ML-like behavior"""
    
    def __init__(self):
        # SMB-focused categories with pattern matching
        self.categories = {
            # Revenue categories
            'Revenue - Sales': [
                r'payment.*received', r'invoice.*paid', r'stripe.*payment',
                r'paypal.*payment', r'square.*payment', r'sales.*revenue',
                r'customer.*payment', r'deposit.*sales'
            ],
            'Revenue - Services': [
                r'consulting.*fee', r'service.*payment', r'hourly.*billing',
                r'professional.*services', r'maintenance.*contract'
            ],
            
            # Operating expenses
            'Office Expenses': [
                r'office.*supplies', r'staples', r'office.*depot', r'amazon.*business',
                r'paper', r'printer.*ink', r'desk', r'chair', r'computer.*equipment'
            ],
            'Software & Technology': [
                r'microsoft.*365', r'google.*workspace', r'adobe', r'slack', r'zoom',
                r'dropbox', r'aws', r'azure', r'software.*license', r'saas', r'subscription'
            ],
            'Marketing & Advertising': [
                r'google.*ads', r'facebook.*ads', r'linkedin.*ads', r'marketing.*campaign',
                r'advertising', r'promotional', r'social.*media', r'seo.*services'
            ],
            'Professional Services': [
                r'legal.*fees', r'attorney', r'lawyer', r'accountant', r'cpa',
                r'consulting', r'professional.*services', r'tax.*preparation'
            ],
            'Utilities': [
                r'electric', r'gas.*bill', r'water.*bill', r'internet', r'phone.*bill',
                r'cellular', r'verizon', r'att', r'comcast', r'utility.*payment'
            ],
            'Rent & Facilities': [
                r'rent.*payment', r'lease.*payment', r'facility.*rent', r'office.*rent',
                r'warehouse.*rent', r'storage.*rent', r'property.*management'
            ],
            'Insurance': [
                r'insurance.*premium', r'liability.*insurance', r'business.*insurance',
                r'health.*insurance', r'workers.*comp', r'property.*insurance'
            ],
            'Travel & Transportation': [
                r'airline', r'hotel', r'car.*rental', r'uber', r'lyft', r'taxi',
                r'gas.*station', r'fuel', r'parking', r'toll', r'mileage'
            ],
            'Meals & Entertainment': [
                r'restaurant', r'lunch', r'dinner', r'coffee', r'starbucks',
                r'business.*meal', r'client.*dinner', r'entertainment'
            ],
            'Equipment & Supplies': [
                r'equipment.*purchase', r'machinery', r'tools', r'supplies',
                r'inventory', r'raw.*materials', r'manufacturing.*supplies'
            ],
            'Banking & Fees': [
                r'bank.*fee', r'atm.*fee', r'wire.*fee', r'overdraft',
                r'monthly.*service', r'transaction.*fee', r'credit.*card.*fee'
            ],
            'Taxes': [
                r'tax.*payment', r'irs.*payment', r'state.*tax', r'payroll.*tax',
                r'sales.*tax', r'property.*tax', r'tax.*withholding'
            ],
            'Payroll & Benefits': [
                r'payroll', r'salary', r'wages', r'employee.*benefits',
                r'health.*benefits', r'retirement.*contribution', r'401k'
            ],
            'Loan Payments': [
                r'loan.*payment', r'sba.*loan', r'business.*loan', r'line.*of.*credit',
                r'equipment.*financing', r'mortgage.*payment'
            ]
        }
        
        # Load user-defined rules
        self.user_rules = self._load_user_rules()
        
        # Load learning data from corrections
        self.learning_patterns = self._load_learning_patterns()
    
    def categorize_transaction(self, description: str, amount: float) -> Tuple[str, float, str]:
        """
        Categorize a transaction with confidence score and explanation
        Returns: (category, confidence, explanation)
        """
        description_lower = description.lower().strip()
        
        # Check user-defined rules first (highest priority)
        for rule in self.user_rules:
            if re.search(rule['pattern'], description_lower):
                return (
                    rule['category'], 
                    rule['confidence'],
                    f"Matched user rule: '{rule['pattern']}'"
                )
        
        # Check learned patterns from corrections
        learned_result = self._check_learned_patterns(description_lower)
        if learned_result:
            return learned_result
        
        # Apply built-in pattern matching
        best_match = None
        best_score = 0.0
        matched_patterns = []
        
        for category, patterns in self.categories.items():
            for pattern in patterns:
                if re.search(pattern, description_lower):
                    # Calculate confidence based on pattern specificity
                    confidence = self._calculate_pattern_confidence(pattern, description_lower)
                    matched_patterns.append((category, confidence, pattern))
                    
                    if confidence > best_score:
                        best_score = confidence
                        best_match = (category, confidence, pattern)
        
        if best_match:
            category, confidence, pattern = best_match
            explanation = f"Matched pattern: '{pattern}'"
            
            # Boost confidence if multiple patterns match the same category
            same_category_matches = [m for m in matched_patterns if m[0] == category]
            if len(same_category_matches) > 1:
                confidence = min(0.95, confidence + 0.1 * (len(same_category_matches) - 1))
            
            return (category, confidence, explanation)
        
        # Amount-based categorization for uncategorized transactions
        if amount > 0:
            if amount > 10000:
                return ('Revenue - Large Payment', 0.3, 'Large positive amount suggests revenue')
            else:
                return ('Revenue - Other', 0.2, 'Positive amount suggests revenue')
        else:
            if abs(amount) > 5000:
                return ('Major Expense', 0.3, 'Large negative amount')
            else:
                return ('Other Expenses', 0.2, 'General business expense')
    
    def _calculate_pattern_confidence(self, pattern: str, description: str) -> float:
        """Calculate confidence score based on pattern match quality"""
        # Base confidence
        confidence = 0.7
        
        # Exact word matches increase confidence
        pattern_words = re.findall(r'\w+', pattern.replace('.*', ' '))
        description_words = description.split()
        
        exact_matches = sum(1 for word in pattern_words if word in description_words)
        if exact_matches > 0:
            confidence += 0.1 * exact_matches
        
        # Longer patterns are more specific
        if len(pattern) > 20:
            confidence += 0.05
        elif len(pattern) > 10:
            confidence += 0.02
        
        return min(0.9, confidence)  # Cap at 0.9 for pattern matches
    
    def _load_user_rules(self) -> List[Dict]:
        """Load user-defined categorization rules"""
        try:
            rules = execute_query("SELECT * FROM rules ORDER BY confidence DESC")
            return [
                {
                    'pattern': rule['description_pattern'],
                    'category': rule['category'],
                    'confidence': float(rule['confidence'])
                }
                for rule in rules
            ]
        except:
            return []
    
    def _load_learning_patterns(self) -> Dict[str, Dict]:
        """Load patterns learned from user corrections"""
        try:
            corrections = execute_query("""
                SELECT t.description, c.new_category, COUNT(*) as frequency
                FROM corrections c
                JOIN transactions t ON c.transaction_id = t.id
                GROUP BY LOWER(t.description), c.new_category
                HAVING frequency >= 2
                ORDER BY frequency DESC
            """)
            
            patterns = {}
            for correction in corrections:
                desc_key = correction['description'].lower().strip()
                patterns[desc_key] = {
                    'category': correction['new_category'],
                    'confidence': min(0.85, 0.6 + 0.1 * correction['frequency']),
                    'frequency': correction['frequency']
                }
            
            return patterns
        except:
            return {}
    
    def _check_learned_patterns(self, description: str) -> Optional[Tuple[str, float, str]]:
        """Check if description matches learned patterns from corrections"""
        # Exact match
        if description in self.learning_patterns:
            pattern = self.learning_patterns[description]
            return (
                pattern['category'],
                pattern['confidence'],
                f"Learned from {pattern['frequency']} previous corrections"
            )
        
        # Partial match for similar descriptions
        for learned_desc, pattern in self.learning_patterns.items():
            # Simple similarity check
            if len(description) > 5 and len(learned_desc) > 5:
                common_words = set(description.split()) & set(learned_desc.split())
                if len(common_words) >= 2 and len(common_words) / len(set(description.split())) > 0.5:
                    return (
                        pattern['category'],
                        pattern['confidence'] * 0.8,  # Reduce confidence for partial match
                        f"Similar to learned pattern (freq: {pattern['frequency']})"
                    )
        
        return None
    
    def create_rule(self, description_pattern: str, category: str, confidence: float = 0.95) -> str:
        """Create a new categorization rule"""
        rule_id = generate_id()
        execute_query(
            "INSERT INTO rules (id, description_pattern, category, confidence) VALUES (?, ?, ?, ?)",
            (rule_id, description_pattern, category, confidence)
        )
        
        # Refresh user rules
        self.user_rules = self._load_user_rules()
        
        return rule_id
    
    def record_correction(self, transaction_id: str, old_category: str, new_category: str) -> str:
        """Record a user correction for learning"""
        correction_id = generate_id()
        execute_query(
            "INSERT INTO corrections (id, transaction_id, old_category, new_category) VALUES (?, ?, ?, ?)",
            (correction_id, transaction_id, old_category, new_category)
        )
        
        # Update the transaction
        execute_query(
            "UPDATE transactions SET category = ?, confidence = 1.0 WHERE id = ?",
            (new_category, transaction_id)
        )
        
        # Refresh learning patterns
        self.learning_patterns = self._load_learning_patterns()
        
        return correction_id
    
    def get_category_suggestions(self, partial_category: str) -> List[str]:
        """Get category suggestions for autocomplete"""
        partial_lower = partial_category.lower()
        
        # Get categories from rules and corrections
        all_categories = set()
        
        # Built-in categories
        all_categories.update(self.categories.keys())
        
        # User-defined categories
        for rule in self.user_rules:
            all_categories.add(rule['category'])
        
        # Categories from corrections
        try:
            corrections = execute_query("SELECT DISTINCT new_category FROM corrections")
            for correction in corrections:
                all_categories.add(correction['new_category'])
        except:
            pass
        
        # Filter and sort suggestions
        suggestions = [
            cat for cat in all_categories 
            if partial_lower in cat.lower()
        ]
        
        return sorted(suggestions)[:10]  # Return top 10 matches

# Initialize service
categorization_service = CategorizationService()

# For backward compatibility with server.py
TransactionCategorizer = CategorizationService