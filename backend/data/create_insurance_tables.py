"""
data/create_insurance_tables.py
───────────────────────────────
Creates insurance-related tables in the database.
Run this to add insurance functionality to existing database.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.db import engine
from database.models import Base, InsurancePolicy, InsuranceRiskAssessment

def create_insurance_tables():
    """Create insurance tables if they don't exist."""
    print("Creating insurance tables...")
    
    # Create only the insurance tables
    InsurancePolicy.__table__.create(engine, checkfirst=True)
    InsuranceRiskAssessment.__table__.create(engine, checkfirst=True)
    
    print("✅ Insurance tables created successfully!")

if __name__ == "__main__":
    create_insurance_tables()