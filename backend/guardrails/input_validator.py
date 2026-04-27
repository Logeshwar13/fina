"""
Input Validator
Validates and sanitizes user inputs before processing.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal, InvalidOperation


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class InputValidator:
    """
    Validates user inputs for safety and correctness.
    """
    
    # Financial limits (in INR)
    MIN_TRANSACTION = Decimal("0")
    MAX_TRANSACTION = Decimal("100000000")  # 10 crore
    MIN_BUDGET = Decimal("100")
    MAX_BUDGET = Decimal("5000000")  # 50 lakh
    MIN_INSURANCE = Decimal("100000")  # 1 lakh
    MAX_INSURANCE = Decimal("100000000")  # 10 crore
    
    # Query limits
    MAX_QUERY_LENGTH = 1000
    MAX_CONTEXT_LENGTH = 5000
    
    # Forbidden patterns
    FORBIDDEN_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # XSS
        r"javascript:",  # JavaScript injection
        r"on\w+\s*=",  # Event handlers
        r"eval\s*\(",  # Code execution
        r"exec\s*\(",  # Code execution
        r"__import__",  # Python imports
        r"DROP\s+TABLE",  # SQL injection
        r"DELETE\s+FROM",  # SQL injection
        r"INSERT\s+INTO",  # SQL injection
        r"UPDATE\s+SET",  # SQL injection
    ]
    
    # Forbidden topics
    FORBIDDEN_TOPICS = [
        "tax evasion",
        "money laundering",
        "illegal",
        "hack",
        "steal",
        "fraud scheme",
        "ponzi",
        "pyramid scheme",
        "insider trading",
        "market manipulation"
    ]
    
    def __init__(self):
        """Initialize input validator"""
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.FORBIDDEN_PATTERNS
        ]
    
    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user query for safety.
        
        Args:
            query: User query string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not query or not query.strip():
            return False, "Query cannot be empty"
        
        # Check length
        if len(query) > self.MAX_QUERY_LENGTH:
            return False, f"Query too long (max {self.MAX_QUERY_LENGTH} characters)"
        
        # Check for injection attacks
        for pattern in self.compiled_patterns:
            if pattern.search(query):
                return False, "Query contains forbidden patterns"
        
        # Check for forbidden topics
        query_lower = query.lower()
        for topic in self.FORBIDDEN_TOPICS:
            if topic in query_lower:
                return False, f"Query contains forbidden topic: {topic}"
        
        return True, None
    
    def validate_amount(
        self,
        amount: Any,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        field_name: str = "amount"
    ) -> Tuple[bool, Optional[str], Optional[Decimal]]:
        """
        Validate financial amount.
        
        Args:
            amount: Amount to validate
            min_amount: Minimum allowed amount
            max_amount: Maximum allowed amount
            field_name: Name of field for error messages
            
        Returns:
            Tuple of (is_valid, error_message, parsed_amount)
        """
        try:
            # Convert to Decimal
            if isinstance(amount, str):
                # Remove currency symbols and commas
                amount = amount.replace("₹", "").replace(",", "").strip()
            
            parsed = Decimal(str(amount))
            
            # Check if negative
            if parsed < 0:
                return False, f"{field_name} cannot be negative", None
            
            # Check minimum
            min_val = min_amount or self.MIN_TRANSACTION
            if parsed < min_val:
                return False, f"{field_name} must be at least ₹{min_val}", None
            
            # Check maximum
            max_val = max_amount or self.MAX_TRANSACTION
            if parsed > max_val:
                return False, f"{field_name} cannot exceed ₹{max_val}", None
            
            return True, None, parsed
            
        except (InvalidOperation, ValueError, TypeError):
            return False, f"Invalid {field_name} format", None
    
    def validate_transaction(self, transaction: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate transaction data.
        
        Args:
            transaction: Transaction dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        required_fields = ["amount", "category", "description"]
        for field in required_fields:
            if field not in transaction:
                return False, f"Missing required field: {field}"
        
        # Validate amount
        is_valid, error, _ = self.validate_amount(
            transaction["amount"],
            self.MIN_TRANSACTION,
            self.MAX_TRANSACTION,
            "Transaction amount"
        )
        if not is_valid:
            return False, error
        
        # Validate category
        if not isinstance(transaction["category"], str):
            return False, "Category must be a string"
        
        if len(transaction["category"]) > 50:
            return False, "Category name too long (max 50 characters)"
        
        # Validate description
        if not isinstance(transaction["description"], str):
            return False, "Description must be a string"
        
        if len(transaction["description"]) > 500:
            return False, "Description too long (max 500 characters)"
        
        # Check for injection in description
        is_valid, error = self.validate_query(transaction["description"])
        if not is_valid:
            return False, f"Invalid description: {error}"
        
        return True, None
    
    def validate_budget(self, budget: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate budget data.
        
        Args:
            budget: Budget dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        required_fields = ["category", "limit"]
        for field in required_fields:
            if field not in budget:
                return False, f"Missing required field: {field}"
        
        # Validate limit
        is_valid, error, _ = self.validate_amount(
            budget["limit"],
            self.MIN_BUDGET,
            self.MAX_BUDGET,
            "Budget limit"
        )
        if not is_valid:
            return False, error
        
        # Validate category
        if not isinstance(budget["category"], str):
            return False, "Category must be a string"
        
        if len(budget["category"]) > 50:
            return False, "Category name too long (max 50 characters)"
        
        return True, None
    
    def validate_insurance(self, insurance: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate insurance data.
        
        Args:
            insurance: Insurance dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        required_fields = ["policy_type", "coverage_amount", "premium"]
        for field in required_fields:
            if field not in insurance:
                return False, f"Missing required field: {field}"
        
        # Validate coverage amount
        is_valid, error, _ = self.validate_amount(
            insurance["coverage_amount"],
            self.MIN_INSURANCE,
            self.MAX_INSURANCE,
            "Coverage amount"
        )
        if not is_valid:
            return False, error
        
        # Validate premium
        is_valid, error, _ = self.validate_amount(
            insurance["premium"],
            self.MIN_TRANSACTION,
            self.MAX_TRANSACTION,
            "Premium amount"
        )
        if not is_valid:
            return False, error
        
        # Validate policy type
        valid_types = ["life", "health", "term", "vehicle", "property"]
        if insurance["policy_type"].lower() not in valid_types:
            return False, f"Invalid policy type. Must be one of: {', '.join(valid_types)}"
        
        return True, None
    
    def validate_risk_score(self, score: Any) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Validate risk score.
        
        Args:
            score: Risk score to validate
            
        Returns:
            Tuple of (is_valid, error_message, parsed_score)
        """
        try:
            parsed = int(score)
            
            if parsed < 0 or parsed > 100:
                return False, "Risk score must be between 0 and 100", None
            
            return True, None, parsed
            
        except (ValueError, TypeError):
            return False, "Invalid risk score format", None
    
    def validate_context(self, context: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate execution context.
        
        Args:
            context: Context dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check user_id
        if "user_id" not in context:
            return False, "Missing user_id in context"
        
        user_id = context["user_id"]
        if not isinstance(user_id, str) or not user_id.strip():
            return False, "Invalid user_id"
        
        # Validate user_id format (alphanumeric, underscore, hyphen)
        if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
            return False, "user_id contains invalid characters"
        
        if len(user_id) > 100:
            return False, "user_id too long (max 100 characters)"
        
        return True, None
    
    def sanitize_query(self, query: str) -> str:
        """
        Sanitize user query by removing potentially harmful content.
        
        Args:
            query: User query
            
        Returns:
            Sanitized query
        """
        # Remove HTML tags
        sanitized = re.sub(r'<[^>]+>', '', query)
        
        # Remove multiple spaces
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Trim
        sanitized = sanitized.strip()
        
        return sanitized
    
    def validate_and_sanitize(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], str]:
        """
        Validate and sanitize query in one step.
        
        Args:
            query: User query
            context: Optional context
            
        Returns:
            Tuple of (is_valid, error_message, sanitized_query)
        """
        # Sanitize first
        sanitized = self.sanitize_query(query)
        
        # Validate sanitized query
        is_valid, error = self.validate_query(sanitized)
        if not is_valid:
            return False, error, sanitized
        
        # Validate context if provided
        if context:
            is_valid, error = self.validate_context(context)
            if not is_valid:
                return False, error, sanitized
        
        return True, None, sanitized
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get summary of validation rules.
        
        Returns:
            Dictionary of validation rules
        """
        return {
            "limits": {
                "transaction": {
                    "min": float(self.MIN_TRANSACTION),
                    "max": float(self.MAX_TRANSACTION)
                },
                "budget": {
                    "min": float(self.MIN_BUDGET),
                    "max": float(self.MAX_BUDGET)
                },
                "insurance": {
                    "min": float(self.MIN_INSURANCE),
                    "max": float(self.MAX_INSURANCE)
                },
                "risk_score": {
                    "min": 0,
                    "max": 100
                }
            },
            "query_limits": {
                "max_length": self.MAX_QUERY_LENGTH,
                "max_context_length": self.MAX_CONTEXT_LENGTH
            },
            "forbidden_topics": self.FORBIDDEN_TOPICS
        }
