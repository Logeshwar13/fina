"""
MCP Guardrails
==============
Input/output validation and safety constraints.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class SafetyLevel(Enum):
    """Safety check severity levels."""
    BLOCK = "block"  # Block the request/response
    WARN = "warn"    # Log warning but allow
    INFO = "info"    # Informational only


class InputValidator:
    """
    Validates user inputs before processing.
    Prevents injection attacks, invalid data, and unsafe queries.
    """
    
    # Financial limits (in INR)
    MAX_TRANSACTION_AMOUNT = 10_00_00_000  # 10 crores
    MAX_BUDGET_LIMIT = 50_00_000           # 50 lakhs
    MAX_INSURANCE_COVERAGE = 10_00_00_000  # 10 crores
    MIN_TRANSACTION_AMOUNT = 0
    MIN_BUDGET_LIMIT = 100
    MIN_INSURANCE_COVERAGE = 1_00_000      # 1 lakh
    
    # Forbidden patterns
    FORBIDDEN_PATTERNS = [
        r"(?i)(drop|delete|truncate)\s+(table|database)",  # SQL injection
        r"(?i)<script[^>]*>.*?</script>",                  # XSS
        r"(?i)union\s+select",                             # SQL injection
        r"(?i)exec\s*\(",                                  # Code execution
        r"(?i)eval\s*\(",                                  # Code execution
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
        "pyramid scheme"
    ]
    
    @classmethod
    def validate_amount(cls, amount: float, context: str = "transaction") -> Tuple[bool, Optional[str]]:
        """
        Validate financial amount.
        
        Returns:
            (is_valid, error_message)
        """
        if context == "transaction":
            if amount < cls.MIN_TRANSACTION_AMOUNT:
                return False, f"Transaction amount cannot be negative"
            if amount > cls.MAX_TRANSACTION_AMOUNT:
                return False, f"Transaction amount exceeds maximum limit of ₹{cls.MAX_TRANSACTION_AMOUNT:,}"
        
        elif context == "budget":
            if amount < cls.MIN_BUDGET_LIMIT:
                return False, f"Budget limit must be at least ₹{cls.MIN_BUDGET_LIMIT}"
            if amount > cls.MAX_BUDGET_LIMIT:
                return False, f"Budget limit exceeds maximum of ₹{cls.MAX_BUDGET_LIMIT:,}"
        
        elif context == "insurance":
            if amount < cls.MIN_INSURANCE_COVERAGE:
                return False, f"Insurance coverage must be at least ₹{cls.MIN_INSURANCE_COVERAGE:,}"
            if amount > cls.MAX_INSURANCE_COVERAGE:
                return False, f"Insurance coverage exceeds maximum of ₹{cls.MAX_INSURANCE_COVERAGE:,}"
        
        return True, None
    
    @classmethod
    def validate_query(cls, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user query for safety.
        
        Returns:
            (is_safe, warning_message)
        """
        query_lower = query.lower()
        
        # Check for forbidden patterns
        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return False, f"Query contains forbidden pattern: {pattern}"
        
        # Check for forbidden topics
        for topic in cls.FORBIDDEN_TOPICS:
            if topic in query_lower:
                return False, f"Query contains forbidden topic: {topic}"
        
        # Check length
        if len(query) > 5000:
            return False, "Query exceeds maximum length of 5000 characters"
        
        return True, None
    
    @classmethod
    def validate_date_range(cls, start_date: str, end_date: str) -> Tuple[bool, Optional[str]]:
        """Validate date range."""
        try:
            start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            
            if start > end:
                return False, "Start date must be before end date"
            
            # Check if range is reasonable (not more than 10 years)
            if (end - start).days > 3650:
                return False, "Date range cannot exceed 10 years"
            
            return True, None
        except Exception as e:
            return False, f"Invalid date format: {str(e)}"
    
    @classmethod
    def validate_user_id(cls, user_id: str) -> Tuple[bool, Optional[str]]:
        """Validate user ID format."""
        if not user_id or not isinstance(user_id, str):
            return False, "User ID is required"
        
        if len(user_id) > 100:
            return False, "User ID too long"
        
        # Check for suspicious patterns
        if re.search(r"[<>\"']", user_id):
            return False, "User ID contains invalid characters"
        
        return True, None
    
    @classmethod
    def sanitize_input(cls, text: str) -> str:
        """Sanitize text input."""
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)
        
        # Remove SQL keywords
        text = re.sub(r"(?i)\b(drop|delete|truncate|union|exec|eval)\b", "[REMOVED]", text)
        
        # Trim whitespace
        text = text.strip()
        
        return text


class OutputValidator:
    """
    Validates LLM outputs before sending to user.
    Prevents hallucinations, unsafe advice, and out-of-range values.
    """
    
    # Forbidden advice patterns
    FORBIDDEN_ADVICE = [
        r"(?i)guaranteed?\s+(profit|return|gain)",
        r"(?i)risk-free\s+investment",
        r"(?i)get\s+rich\s+quick",
        r"(?i)100%\s+(safe|secure|guaranteed)",
        r"(?i)no\s+risk",
        r"(?i)tax\s+evasion",
        r"(?i)hide\s+(money|income|assets)",
    ]
    
    # Required disclaimers for certain topics
    DISCLAIMER_TRIGGERS = {
        "investment": "This is not financial advice. Consult a certified financial advisor.",
        "tax": "This is general information only. Consult a tax professional for your specific situation.",
        "insurance": "Insurance needs vary by individual. Consult an insurance advisor for personalized recommendations.",
        "loan": "Loan terms and eligibility vary. Contact lenders directly for accurate information."
    }
    
    @classmethod
    def validate_response(cls, response: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate LLM response.
        
        Returns:
            (is_safe, error_message, modified_response)
        """
        # Check for forbidden advice
        for pattern in cls.FORBIDDEN_ADVICE:
            if re.search(pattern, response, re.IGNORECASE):
                return False, f"Response contains forbidden advice pattern: {pattern}", None
        
        # Check for hallucinated numbers
        numbers = re.findall(r"₹\s*[\d,]+(?:\.\d+)?", response)
        for num_str in numbers:
            try:
                num = float(num_str.replace("₹", "").replace(",", "").strip())
                if num > 100_00_00_000:  # 100 crores
                    return False, f"Response contains unrealistic amount: {num_str}", None
            except:
                pass
        
        # Add disclaimers if needed
        modified_response = response
        for trigger, disclaimer in cls.DISCLAIMER_TRIGGERS.items():
            if trigger in response.lower() and disclaimer not in response:
                modified_response += f"\n\n⚠️ {disclaimer}"
        
        return True, None, modified_response
    
    @classmethod
    def validate_financial_advice(cls, advice: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate structured financial advice."""
        # Check for unrealistic returns
        if "expected_return" in advice:
            ret = advice["expected_return"]
            if isinstance(ret, (int, float)) and ret > 50:  # >50% return
                return False, "Expected return is unrealistically high"
        
        # Check for zero-risk claims
        if "risk_level" in advice:
            risk = str(advice["risk_level"]).lower()
            if risk in ["none", "zero", "no risk"]:
                return False, "Cannot claim zero risk"
        
        # Check amounts are in valid ranges
        if "amount" in advice:
            is_valid, error = InputValidator.validate_amount(advice["amount"])
            if not is_valid:
                return False, error
        
        return True, None


class PromptConstraints:
    """
    System prompt constraints and safety rules.
    """
    
    SYSTEM_CONSTRAINTS = """
You are a helpful financial assistant. You MUST follow these rules:

1. NEVER guarantee investment returns or claim zero risk
2. NEVER provide tax evasion advice or illegal financial strategies
3. NEVER recommend specific stocks, cryptocurrencies, or individual securities
4. ALWAYS include appropriate disclaimers for financial advice
5. ALWAYS verify amounts are within reasonable ranges (₹0 - ₹10 crores)
6. NEVER fabricate financial data - only use provided context
7. ALWAYS recommend consulting certified professionals for major decisions
8. NEVER encourage excessive debt or risky financial behavior

If asked about illegal activities, politely decline and explain why.
If asked for guarantees, explain that all investments carry risk.
If data is missing, say "I don't have that information" rather than guessing.
"""
    
    AGENT_SPECIFIC_CONSTRAINTS = {
        "budget": """
Focus on:
- Realistic budget limits (₹100 - ₹50 lakhs per category)
- Sustainable spending habits
- Emergency fund building (3-6 months expenses)

Avoid:
- Extreme frugality that's unsustainable
- Unrealistic savings targets
""",
        "fraud": """
Focus on:
- Pattern recognition in transactions
- Security best practices
- Legitimate fraud indicators

Avoid:
- False positives that cause panic
- Accusing specific merchants without evidence
""",
        "risk": """
Focus on:
- Balanced risk assessment
- Actionable improvement steps
- Long-term financial health

Avoid:
- Overly pessimistic assessments
- Unrealistic quick fixes
""",
        "investment": """
Focus on:
- Diversification principles
- Risk tolerance assessment
- Long-term wealth building

Avoid:
- Specific stock recommendations
- Market timing advice
- Get-rich-quick schemes
""",
        "insurance": """
Focus on:
- Coverage adequacy assessment
- Life stage appropriate recommendations
- Risk mitigation strategies

Avoid:
- Specific policy recommendations
- Pressure to over-insure
- Unrealistic coverage amounts
"""
    }
    
    @classmethod
    def get_system_prompt(cls, agent_type: Optional[str] = None) -> str:
        """Get system prompt with constraints."""
        prompt = cls.SYSTEM_CONSTRAINTS
        
        if agent_type and agent_type in cls.AGENT_SPECIFIC_CONSTRAINTS:
            prompt += f"\n\nAgent-specific guidelines:\n{cls.AGENT_SPECIFIC_CONSTRAINTS[agent_type]}"
        
        return prompt


class GuardrailsEngine:
    """
    Main guardrails engine that orchestrates all validation.
    """
    
    def __init__(self):
        self.input_validator = InputValidator()
        self.output_validator = OutputValidator()
        self.violations_log: List[Dict[str, Any]] = []
    
    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate all inputs.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate user_id if present
        if "user_id" in data:
            is_valid, error = self.input_validator.validate_user_id(data["user_id"])
            if not is_valid:
                errors.append(error)
        
        # Validate query if present
        if "query" in data:
            is_safe, warning = self.input_validator.validate_query(data["query"])
            if not is_safe:
                errors.append(warning)
                self._log_violation("input", "query", warning)
        
        # Validate amounts
        for key in ["amount", "limit", "coverage"]:
            if key in data:
                context = "transaction" if key == "amount" else "budget" if key == "limit" else "insurance"
                is_valid, error = self.input_validator.validate_amount(data[key], context)
                if not is_valid:
                    errors.append(error)
        
        # Validate date ranges
        if "start_date" in data and "end_date" in data:
            is_valid, error = self.input_validator.validate_date_range(data["start_date"], data["end_date"])
            if not is_valid:
                errors.append(error)
        
        return len(errors) == 0, errors
    
    def validate_output(self, response: str) -> Tuple[bool, Optional[str], str]:
        """
        Validate LLM output.
        
        Returns:
            (is_safe, error_message, modified_response)
        """
        is_safe, error, modified = self.output_validator.validate_response(response)
        
        if not is_safe:
            self._log_violation("output", "response", error)
        
        return is_safe, error, modified or response
    
    def _log_violation(self, violation_type: str, field: str, message: str):
        """Log a guardrail violation."""
        self.violations_log.append({
            "type": violation_type,
            "field": field,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_violations(self) -> List[Dict[str, Any]]:
        """Get all logged violations."""
        return self.violations_log
    
    def clear_violations(self):
        """Clear violation log."""
        self.violations_log = []


# Global guardrails instance
guardrails = GuardrailsEngine()
