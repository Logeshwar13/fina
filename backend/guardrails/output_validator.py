"""
Output Validator
Validates and filters AI-generated outputs for safety and accuracy.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal


class OutputValidator:
    """
    Validates AI-generated outputs for safety and compliance.
    """
    
    # Forbidden phrases in outputs
    FORBIDDEN_PHRASES = [
        "guaranteed returns",
        "risk-free investment",
        "100% profit",
        "get rich quick",
        "no risk",
        "guaranteed profit",
        "tax evasion",
        "avoid taxes illegally",
        "hide income",
        "offshore account to avoid",
        "insider information",
        "market manipulation",
        "pump and dump"
    ]
    
    # Warning phrases that need disclaimers
    WARNING_PHRASES = [
        "invest",
        "investment",
        "stock",
        "mutual fund",
        "returns",
        "profit",
        "tax",
        "insurance claim"
    ]
    
    # Required disclaimers
    DISCLAIMERS = {
        "investment": "\n\n⚠️ Disclaimer: Investment advice is for informational purposes only. Past performance does not guarantee future results. Please consult a certified financial advisor before making investment decisions.",
        "tax": "\n\n⚠️ Disclaimer: Tax information is general in nature. Please consult a tax professional for advice specific to your situation.",
        "insurance": "\n\n⚠️ Disclaimer: Insurance recommendations are general guidelines. Please review policy terms and consult an insurance advisor before purchasing."
    }
    
    def __init__(self):
        """Initialize output validator"""
        self.compiled_forbidden = [
            re.compile(phrase, re.IGNORECASE)
            for phrase in self.FORBIDDEN_PHRASES
        ]
    
    def validate_response(self, response: str) -> Tuple[bool, Optional[str]]:
        """
        Validate AI response for safety.
        
        Args:
            response: AI-generated response
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not response or not response.strip():
            return False, "Response cannot be empty"
        
        # Check for forbidden phrases
        response_lower = response.lower()
        for pattern in self.compiled_forbidden:
            if pattern.search(response):
                return False, "Response contains forbidden content"
        
        # Check length (reasonable response)
        if len(response) > 5000:
            return False, "Response too long (max 5000 characters)"
        
        return True, None
    
    def validate_financial_advice(
        self,
        response: str,
        amounts: Optional[List[Decimal]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate financial advice for reasonableness.
        
        Args:
            response: AI-generated financial advice
            amounts: List of amounts mentioned in response
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation
        is_valid, error = self.validate_response(response)
        if not is_valid:
            return False, error
        
        # Check for unrealistic amounts
        if amounts:
            for amount in amounts:
                if amount > Decimal("100000000"):  # 10 crore
                    return False, "Response contains unrealistic amounts"
                if amount < 0:
                    return False, "Response contains negative amounts"
        
        # Check for percentage claims
        percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', response)
        for pct_str in percentages:
            pct = float(pct_str)
            # Flag unrealistic returns
            if pct > 50:  # More than 50% returns
                return False, "Response contains unrealistic return percentages"
        
        return True, None
    
    def detect_hallucination(self, response: str, context: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Detect potential hallucinations in response.
        
        Args:
            response: AI-generated response
            context: Context used to generate response
            
        Returns:
            Tuple of (has_hallucination, description)
        """
        # Check for specific data claims without context
        data_patterns = [
            r'you spent ₹[\d,]+',
            r'your balance is ₹[\d,]+',
            r'you have \d+ transactions',
            r'your budget is ₹[\d,]+'
        ]
        
        response_lower = response.lower()
        
        # If response makes specific claims but context is empty
        if not context or not context.get("has_data"):
            for pattern in data_patterns:
                if re.search(pattern, response_lower):
                    return True, "Response makes specific claims without supporting data"
        
        # Check for contradictions
        if "no transactions" in response_lower and "you spent" in response_lower:
            return True, "Response contains contradictory statements"
        
        return False, None
    
    def add_disclaimers(self, response: str) -> str:
        """
        Add appropriate disclaimers to response.
        
        Args:
            response: AI-generated response
            
        Returns:
            Response with disclaimers added
        """
        response_lower = response.lower()
        added_disclaimers = []
        
        # Check for investment advice
        if any(phrase in response_lower for phrase in ["invest", "investment", "stock", "mutual fund", "returns"]):
            if "investment" not in added_disclaimers:
                response += self.DISCLAIMERS["investment"]
                added_disclaimers.append("investment")
        
        # Check for tax advice
        if "tax" in response_lower:
            if "tax" not in added_disclaimers:
                response += self.DISCLAIMERS["tax"]
                added_disclaimers.append("tax")
        
        # Check for insurance advice
        if "insurance" in response_lower or "policy" in response_lower:
            if "insurance" not in added_disclaimers:
                response += self.DISCLAIMERS["insurance"]
                added_disclaimers.append("insurance")
        
        return response
    
    def filter_sensitive_data(self, response: str) -> str:
        """
        Filter out sensitive data from response.
        
        Args:
            response: AI-generated response
            
        Returns:
            Filtered response
        """
        # Mask credit card numbers (keep last 4 digits)
        response = re.sub(
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?(\d{4})\b',
            r'****-****-****-\1',
            response
        )
        
        # Mask account numbers (keep last 4 digits)
        response = re.sub(
            r'\b\d{8,16}\b',
            lambda m: '*' * (len(m.group()) - 4) + m.group()[-4:],
            response
        )
        
        # Mask PAN numbers
        response = re.sub(
            r'\b[A-Z]{5}\d{4}[A-Z]\b',
            'XXXXX****X',
            response
        )
        
        # Mask Aadhaar numbers
        response = re.sub(
            r'\b\d{4}[\s-]?\d{4}[\s-]?(\d{4})\b',
            r'****-****-\1',
            response
        )
        
        return response
    
    def validate_risk_assessment(
        self,
        response: str,
        risk_score: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate risk assessment response.
        
        Args:
            response: AI-generated risk assessment
            risk_score: Risk score mentioned in response
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation
        is_valid, error = self.validate_response(response)
        if not is_valid:
            return False, error
        
        # Validate risk score if provided
        if risk_score is not None:
            if risk_score < 0 or risk_score > 100:
                return False, "Invalid risk score in response"
        
        # Check for balanced assessment
        response_lower = response.lower()
        
        # Risk assessment should mention both positives and concerns
        has_positive = any(word in response_lower for word in ["good", "healthy", "strong", "positive"])
        has_concern = any(word in response_lower for word in ["concern", "risk", "issue", "problem", "warning"])
        
        # If score is extreme (very low or very high), should have appropriate tone
        if risk_score is not None:
            if risk_score < 30 and not has_positive:
                return False, "Low risk score should have positive tone"
            if risk_score > 70 and not has_concern:
                return False, "High risk score should mention concerns"
        
        return True, None
    
    def validate_budget_advice(self, response: str) -> Tuple[bool, Optional[str]]:
        """
        Validate budget advice response.
        
        Args:
            response: AI-generated budget advice
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation
        is_valid, error = self.validate_response(response)
        if not is_valid:
            return False, error
        
        response_lower = response.lower()
        
        # Budget advice should be actionable
        has_action = any(word in response_lower for word in [
            "reduce", "increase", "save", "cut", "allocate", "adjust", "consider", "try"
        ])
        
        if not has_action:
            return False, "Budget advice should include actionable recommendations"
        
        # Should not be overly restrictive
        extreme_words = ["never", "always", "must", "forbidden", "prohibited"]
        extreme_count = sum(1 for word in extreme_words if word in response_lower)
        
        if extreme_count > 2:
            return False, "Budget advice is too restrictive"
        
        return True, None
    
    def validate_fraud_alert(self, response: str) -> Tuple[bool, Optional[str]]:
        """
        Validate fraud alert response.
        
        Args:
            response: AI-generated fraud alert
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation
        is_valid, error = self.validate_response(response)
        if not is_valid:
            return False, error
        
        response_lower = response.lower()
        
        # Fraud alerts should be clear about severity
        if "suspicious" in response_lower or "fraud" in response_lower:
            # Should provide next steps
            has_action = any(phrase in response_lower for phrase in [
                "contact", "verify", "check", "review", "investigate", "report"
            ])
            
            if not has_action:
                return False, "Fraud alert should include recommended actions"
        
        return True, None
    
    def sanitize_output(self, response: str) -> str:
        """
        Sanitize output by removing/filtering problematic content.
        
        Args:
            response: AI-generated response
            
        Returns:
            Sanitized response
        """
        # Filter sensitive data
        sanitized = self.filter_sensitive_data(response)
        
        # Remove excessive punctuation
        sanitized = re.sub(r'[!]{3,}', '!!', sanitized)
        sanitized = re.sub(r'[?]{3,}', '??', sanitized)
        
        # Remove excessive capitalization
        words = sanitized.split()
        sanitized = ' '.join(
            word if not word.isupper() or len(word) <= 3 else word.capitalize()
            for word in words
        )
        
        # Trim excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)
        sanitized = sanitized.strip()
        
        return sanitized
    
    def validate_and_enhance(
        self,
        response: str,
        response_type: str = "general",
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], str]:
        """
        Validate and enhance response in one step.
        
        Args:
            response: AI-generated response
            response_type: Type of response (general, financial, risk, budget, fraud)
            context: Optional context
            
        Returns:
            Tuple of (is_valid, error_message, enhanced_response)
        """
        # Validate based on type
        if response_type == "financial":
            is_valid, error = self.validate_financial_advice(response)
        elif response_type == "risk":
            is_valid, error = self.validate_risk_assessment(response)
        elif response_type == "budget":
            is_valid, error = self.validate_budget_advice(response)
        elif response_type == "fraud":
            is_valid, error = self.validate_fraud_alert(response)
        else:
            is_valid, error = self.validate_response(response)
        
        if not is_valid:
            return False, error, response
        
        # Check for hallucinations
        if context:
            has_hallucination, desc = self.detect_hallucination(response, context)
            if has_hallucination:
                return False, f"Potential hallucination: {desc}", response
        
        # Sanitize
        enhanced = self.sanitize_output(response)
        
        # Add disclaimers
        enhanced = self.add_disclaimers(enhanced)
        
        return True, None, enhanced
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get summary of validation rules.
        
        Returns:
            Dictionary of validation rules
        """
        return {
            "forbidden_phrases": self.FORBIDDEN_PHRASES,
            "warning_phrases": self.WARNING_PHRASES,
            "disclaimers": list(self.DISCLAIMERS.keys()),
            "max_response_length": 5000,
            "filters": [
                "sensitive_data",
                "excessive_punctuation",
                "excessive_capitalization"
            ]
        }
