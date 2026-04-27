"""
Fraud Detection Agent
Specializes in identifying suspicious transactions and security threats.
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentRole


class FraudAgent(BaseAgent):
    """
    Fraud detection and security specialist.
    Identifies suspicious patterns, flags anomalies, and provides security recommendations.
    """
    
    def __init__(self, model_layer, protocol_layer, rag_pipeline=None):
        """Initialize Fraud Agent"""
        super().__init__(
            name="Fraud Detector",
            role=AgentRole.FRAUD_DETECTOR,
            model_layer=model_layer,
            protocol_layer=protocol_layer,
            rag_pipeline=rag_pipeline
        )
        
        # Fraud-specific tools - ACCESS ALL DATA
        self.tools = [
            "get_fraud_alerts",
            "get_transactions",
            "get_transaction_stats",
            "get_last_transaction",
            "get_transactions_by_date_range",
            "flag_transaction_safe",
            "flag_transaction_fraud",
            "get_budgets",
            "get_risk_score",
            "get_insurance_policies",
            "get_spending_insights",
            "create_budget",
            "create_transaction",
            "update_budget",
            "delete_budget",
            "delete_transaction"
        ]
        
        # Fraud detection thresholds
        self.thresholds = {
            "high_amount": 50000,  # ₹50,000
            "unusual_time": (22, 6),  # 10 PM to 6 AM
            "rapid_transactions": 5,  # 5 transactions in short time
            "foreign_transaction": True
        }
    
    async def analyze_transaction_security(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze recent transactions for security issues.
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Security analysis
        """
        context = {"user_id": user_id}
        
        # Get recent transactions
        txn_result = await self.protocol.registry.execute_tool(
            name="get_transactions",
            arguments={"user_id": user_id, "limit": 200},
            context=context
        )
        
        # Get fraud alerts
        alerts_result = await self.protocol.registry.execute_tool(
            name="get_fraud_alerts",
            arguments={"user_id": user_id},
            context=context
        )
        
        transactions = txn_result.get("transactions", [])
        alerts = alerts_result.get("alerts", [])
        
        # Analyze patterns
        analysis = self._detect_patterns(transactions)
        
        # Generate report with LLM
        prompt = f"""Analyze transaction security and fraud risk.

Total Transactions: {len(transactions)}
Fraud Alerts: {len(alerts)}
Pattern Analysis: {analysis}

Provide:
1. Overall security assessment (Low/Medium/High risk)
2. Suspicious patterns identified
3. Specific transactions of concern
4. Recommended security actions
5. Prevention tips

Be specific and actionable."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.3,
            max_tokens=600
        )
        
        return {
            "security_report": response["content"],
            "transactions_analyzed": len(transactions),
            "alerts_found": len(alerts),
            "patterns": analysis
        }
    
    def _detect_patterns(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect suspicious patterns in transactions"""
        patterns = {
            "high_amount_count": 0,
            "unusual_time_count": 0,
            "duplicate_merchants": [],
            "rapid_sequence": False,
            "categories_flagged": []
        }
        
        # Analyze each transaction
        for txn in transactions:
            amount = txn.get("amount", 0)
            
            # High amount transactions
            if amount > self.thresholds["high_amount"]:
                patterns["high_amount_count"] += 1
            
            # Check for unusual categories
            category = txn.get("category", "")
            if category in ["Unknown", "Other"]:
                patterns["categories_flagged"].append(txn.get("id"))
        
        return patterns
    
    async def investigate_alert(
        self,
        user_id: str,
        alert_id: str
    ) -> Dict[str, Any]:
        """
        Investigate a specific fraud alert.
        
        Args:
            user_id: User ID
            alert_id: Alert ID to investigate
            
        Returns:
            Investigation results
        """
        context = {"user_id": user_id}
        
        # Get alert details
        alerts_result = await self.protocol.registry.execute_tool(
            name="get_fraud_alerts",
            arguments={"user_id": user_id},
            context=context
        )
        
        alerts = alerts_result.get("alerts", [])
        alert = next((a for a in alerts if a.get("id") == alert_id), None)
        
        if not alert:
            return {"error": "Alert not found"}
        
        # Investigate with LLM
        prompt = f"""Investigate this fraud alert in detail.

Alert Details: {alert}

Provide:
1. Likelihood of fraud (percentage)
2. Evidence supporting/refuting fraud
3. Similar patterns in history
4. Recommended action (approve/block/review)
5. Reasoning for recommendation

Be thorough and objective."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.2,
            max_tokens=500
        )
        
        return {
            "investigation": response["content"],
            "alert": alert
        }
    
    async def generate_security_recommendations(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Generate personalized security recommendations.
        
        Args:
            user_id: User ID
            
        Returns:
            Security recommendations
        """
        # Analyze security posture
        analysis = await self.analyze_transaction_security(user_id)
        
        # Generate recommendations
        prompt = f"""Based on the security analysis, provide recommendations.

Security Analysis: {analysis['security_report']}

Provide:
1. Top 3 security improvements
2. Account protection tips
3. Transaction monitoring suggestions
4. Emergency response plan
5. Best practices for safe transactions

Make recommendations specific and actionable."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.model.generate(
            messages=messages,
            temperature=0.5,
            max_tokens=600
        )
        
        return {
            "recommendations": response["content"],
            "based_on_analysis": analysis
        }
    
    def _prepare_tool_arguments(self, tool_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare fraud-specific tool arguments"""
        args = super()._prepare_tool_arguments(tool_name, context)
        
        if tool_name == "get_transactions":
            args["limit"] = 200  # More transactions for pattern detection
        
        return args
