"""
AI categorization service for BannkMint AI
"""
import re
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import Transaction, Rule, Correction, Vendor

class TransactionCategorizer:
    """Handles AI-powered transaction categorization"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def extract_vendor_from_description(self, description: str) -> str:
        """Extract vendor name from transaction description"""
        # Clean description
        clean_desc = re.sub(r'\s+', ' ', description.lower().strip())
        
        # Common patterns for vendor extraction
        patterns = [
            r'paypal \*([^0-9\s]+)',  # PayPal transactions
            r'sq \*([^0-9\s]+)',      # Square transactions
            r'tst\* ([^0-9\s]+)',     # Toast transactions
            r'sp \* ([^0-9\s]+)',     # Stripe transactions
            r'^([a-zA-Z\s&]+)',       # First word(s) before numbers
        ]
        
        for pattern in patterns:
            match = re.search(pattern, clean_desc)
            if match:
                vendor = match.group(1).strip()
                if len(vendor) > 2:  # Minimum vendor name length
                    return vendor.title()
        
        # Fallback: take first few words
        words = clean_desc.split()[:3]
        vendor = ' '.join(words)
        
        # Remove common noise words
        noise_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        clean_words = [word for word in words if word not in noise_words and len(word) > 2]
        
        if clean_words:
            return ' '.join(clean_words[:2]).title()
        
        return vendor.title()
    
    def apply_rules(self, description: str, amount: float) -> Tuple[Optional[str], Optional[str], float, str]:
        """Apply categorization rules"""
        # Get active rules ordered by priority
        rules = self.db.query(Rule).filter(
            Rule.active == 1
        ).order_by(Rule.priority.asc()).all()
        
        for rule in rules:
            match = False
            
            if rule.match_type == 'exact':
                match = description.lower() == rule.pattern.lower()
            elif rule.match_type == 'contains':
                match = rule.pattern.lower() in description.lower()
            elif rule.match_type == 'regex':
                try:
                    match = bool(re.search(rule.pattern, description, re.IGNORECASE))
                except re.error:
                    continue  # Skip invalid regex
            
            if match:
                # Update rule hit count
                rule.hits += 1
                self.db.commit()
                
                confidence = 0.97 if rule.match_type == 'exact' else 0.95
                why = f"rule:{rule.pattern}"
                
                return rule.set_category, rule.set_vendor, confidence, why
        
        return None, None, 0.0, ""
    
    def apply_heuristics(self, description: str, amount: float) -> Tuple[Optional[str], Optional[str], float, str]:
        """Apply heuristic categorization"""
        desc_lower = description.lower()
        
        # Define category keywords with confidence scores
        category_keywords = {
            'Software & Technology': {
                'keywords': ['aws', 'amazon web services', 'microsoft', 'adobe', 'saas', 'software', 'cloud', 'hosting', 'domain'],
                'confidence': 0.85
            },
            'Marketing & Advertising': {
                'keywords': ['google ads', 'facebook ads', 'linkedin ads', 'instagram ads', 'marketing', 'advertising', 'promotion'],
                'confidence': 0.88
            },
            'Payment Processing Fees': {
                'keywords': ['stripe', 'paypal', 'square', 'processing fee', 'merchant fee', 'transaction fee'],
                'confidence': 0.90
            },
            'Transportation': {
                'keywords': ['uber', 'lyft', 'taxi', 'gas', 'fuel', 'parking', 'toll', 'mileage'],
                'confidence': 0.82
            },
            'Meals & Entertainment': {
                'keywords': ['restaurant', 'starbucks', 'coffee', 'lunch', 'dinner', 'catering', 'meal'],
                'confidence': 0.80
            },
            'Office Supplies': {
                'keywords': ['office depot', 'staples', 'supplies', 'paper', 'printer', 'ink', 'stationery'],
                'confidence': 0.85
            },
            'Taxes': {
                'keywords': ['irs', 'tax', 'revenue', 'federal', 'state tax', 'payroll tax'],
                'confidence': 0.95
            },
            'Payroll': {
                'keywords': ['gusto', 'adp', 'paychex', 'payroll', 'salary', 'wages', 'employee'],
                'confidence': 0.90
            },
            'Utilities': {
                'keywords': ['electric', 'gas bill', 'water', 'internet', 'phone', 'utilities'],
                'confidence': 0.87
            },
            'Insurance': {
                'keywords': ['insurance', 'premium', 'policy', 'coverage', 'deductible'],
                'confidence': 0.85
            },
            'Professional Services': {
                'keywords': ['legal', 'accounting', 'consulting', 'lawyer', 'attorney', 'cpa'],
                'confidence': 0.83
            },
            'Banking Fees': {
                'keywords': ['bank fee', 'overdraft', 'maintenance fee', 'wire fee', 'atm fee'],
                'confidence': 0.92
            }
        }
        
        # Check each category
        for category, data in category_keywords.items():
            for keyword in data['keywords']:
                if keyword in desc_lower:
                    vendor = self.extract_vendor_from_description(description)
                    confidence = data['confidence']
                    why = f"heuristic:{keyword}"
                    return category, vendor, confidence, why
        
        return None, None, 0.0, ""
    
    def apply_memory(self, vendor: str) -> Tuple[Optional[str], float, str]:
        """Apply memory-based categorization from corrections"""
        if not vendor:
            return None, 0.0, ""
        
        # Find the most common category for this vendor from corrections
        corrections = self.db.query(Correction).join(Transaction).filter(
            Transaction.vendor.ilike(f"%{vendor}%")
        ).all()
        
        if len(corrections) < 3:  # Need at least 3 corrections to trust
            return None, 0.0, ""
        
        # Count category occurrences
        category_counts = {}
        for correction in corrections:
            category = correction.new_category
            if category:
                category_counts[category] = category_counts.get(category, 0) + 1
        
        if not category_counts:
            return None, 0.0, ""
        
        # Get most common category
        most_common_category = max(category_counts, key=category_counts.get)
        confidence_score = min(0.95, 0.8 + (category_counts[most_common_category] * 0.03))
        
        why = f"memory:vendor->{most_common_category}"
        return most_common_category, confidence_score, why
    
    def categorize_transaction(self, transaction: Transaction) -> Dict:
        """Main categorization logic"""
        description = transaction.description
        amount = transaction.amount
        
        # Step 1: Apply rules (highest priority)
        category, vendor, confidence, why = self.apply_rules(description, amount)
        
        if category:
            return {
                'category': category,
                'vendor': vendor or self.extract_vendor_from_description(description),
                'confidence': confidence,
                'why': why
            }
        
        # Step 2: Apply heuristics
        category, vendor, confidence, why = self.apply_heuristics(description, amount)
        
        if category:
            return {
                'category': category,
                'vendor': vendor,
                'confidence': confidence,
                'why': why
            }
        
        # Step 3: Apply memory
        potential_vendor = self.extract_vendor_from_description(description)
        category, confidence, why = self.apply_memory(potential_vendor)
        
        if category:
            return {
                'category': category,
                'vendor': potential_vendor,
                'confidence': confidence,
                'why': why
            }
        
        # Step 4: Default to uncategorized
        return {
            'category': 'Uncategorized',
            'vendor': potential_vendor,
            'confidence': 0.6,
            'why': 'none'
        }
    
    def categorize_batch(self, transaction_ids: List[str]) -> Dict:
        """Categorize multiple transactions"""
        transactions = self.db.query(Transaction).filter(
            Transaction.id.in_(transaction_ids)
        ).all()
        
        results = {'categorized': 0, 'total': len(transactions)}
        
        for transaction in transactions:
            if transaction.category is None:  # Only categorize uncategorized
                result = self.categorize_transaction(transaction)
                
                # Update transaction
                transaction.category = result['category']
                transaction.vendor = result['vendor']
                transaction.confidence = result['confidence']
                transaction.why = result['why']
                
                results['categorized'] += 1
        
        self.db.commit()
        return results
    
    def learn_from_correction(self, transaction_id: str, new_category: str, 
                             new_vendor: str = None, make_rule: bool = False, 
                             pattern: str = None) -> Dict:
        """Learn from user correction"""
        transaction = self.db.query(Transaction).filter(
            Transaction.id == transaction_id
        ).first()
        
        if not transaction:
            return {'success': False, 'error': 'Transaction not found'}
        
        # Record correction
        correction = Correction(
            txn_id=transaction_id,
            old_category=transaction.category,
            new_category=new_category,
            old_vendor=transaction.vendor,
            new_vendor=new_vendor,
            reason="User correction"
        )
        self.db.add(correction)
        
        # Update transaction
        old_category = transaction.category
        transaction.category = new_category
        if new_vendor:
            transaction.vendor = new_vendor
        transaction.confidence = 0.99  # User correction has highest confidence
        transaction.why = "user_correction"
        
        # Create rule if requested
        if make_rule and pattern:
            rule = Rule(
                match_type='contains',
                pattern=pattern.lower(),
                set_category=new_category,
                set_vendor=new_vendor,
                priority=90,  # High priority for user rules
                scope='company'
            )
            self.db.add(rule)
        
        # Check if we should auto-create a rule based on similar corrections
        elif not make_rule:
            similar_corrections = self.db.query(Correction).join(Transaction).filter(
                Transaction.vendor == transaction.vendor,
                Correction.new_category == new_category
            ).count()
            
            if similar_corrections >= 3:  # Auto-promote after 3 corrections
                # Check if rule already exists
                existing_rule = self.db.query(Rule).filter(
                    Rule.pattern == transaction.vendor.lower(),
                    Rule.set_category == new_category
                ).first()
                
                if not existing_rule:
                    auto_rule = Rule(
                        match_type='contains',
                        pattern=transaction.vendor.lower(),
                        set_category=new_category,
                        set_vendor=transaction.vendor,
                        priority=85,  # Slightly lower than manual rules
                        scope='company'
                    )
                    self.db.add(auto_rule)
        
        self.db.commit()
        
        return {
            'success': True,
            'old_category': old_category,
            'new_category': new_category,
            'confidence': transaction.confidence
        }