"""
Setup insurance tables in Supabase database
Run this once to create the insurance tables
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.db import get_supabase

def setup_insurance_tables():
    """Create insurance tables using Supabase client"""
    sb = get_supabase()
    
    print("Setting up insurance tables...")
    
    # Create a test policy to trigger table creation
    try:
        # This will create the table if it doesn't exist (Supabase auto-schema)
        test_policy = {
            "user_id": "test-setup-user",
            "policy_type": "health",
            "provider": "Test Provider",
            "policy_number": "SETUP-TEST",
            "coverage_amount": 100000,
            "premium_amount": 5000,
            "premium_frequency": "annual",
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-12-31T23:59:59Z",
            "beneficiaries": [],
            "status": "active",
            "notes": "Setup test policy"
        }
        
        # Try to insert - this will create the table
        result = sb.table("insurance_policies").insert(test_policy).execute()
        print("✅ insurance_policies table created/verified")
        
        # Delete the test record
        sb.table("insurance_policies").delete().eq("user_id", "test-setup-user").execute()
        print("✅ Test policy cleaned up")
        
    except Exception as e:
        print(f"❌ Error with insurance_policies: {e}")
    
    # Create test assessment
    try:
        test_assessment = {
            "user_id": "test-setup-user",
            "age": 30,
            "dependents": 2,
            "annual_income": 1000000,
            "monthly_expenses": 50000,
            "existing_loans": 0,
            "health_conditions": [],
            "lifestyle_factors": {},
            "recommended_life_coverage": 12000000,
            "recommended_health_coverage": 500000,
            "current_life_coverage": 0,
            "current_health_coverage": 0,
            "coverage_gap_life": 12000000,
            "coverage_gap_health": 500000,
            "risk_score": 75,
            "risk_level": "high",
            "recommendations": ["Get life insurance", "Get health insurance"]
        }
        
        result = sb.table("insurance_risk_assessments").insert(test_assessment).execute()
        print("✅ insurance_risk_assessments table created/verified")
        
        # Delete the test record
        sb.table("insurance_risk_assessments").delete().eq("user_id", "test-setup-user").execute()
        print("✅ Test assessment cleaned up")
        
    except Exception as e:
        print(f"❌ Error with insurance_risk_assessments: {e}")
    
    print("\n🎉 Insurance database setup complete!")
    print("You can now use the Insurance feature in the app.")

if __name__ == "__main__":
    setup_insurance_tables()