"""
Multi-Agent System for Financial Advisory
Specialized agents for different financial domains.
"""

from .base_agent import BaseAgent, AgentRole
from .budget_agent import BudgetAgent
from .fraud_agent import FraudAgent
from .risk_agent import RiskAgent
from .investment_agent import InvestmentAgent
from .insurance_agent import InsuranceAgent

__all__ = [
    "BaseAgent",
    "AgentRole",
    "BudgetAgent",
    "FraudAgent",
    "RiskAgent",
    "InvestmentAgent",
    "InsuranceAgent",
]
