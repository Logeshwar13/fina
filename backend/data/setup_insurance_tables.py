"""
data/setup_insurance_tables.py
──────────────────────────────
Creates insurance tables in Supabase database.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.db import get_supabase

def setup_insurance_tables():
    """Create insurance tables in Supabase."""
    sb = get_supabase()
    
    # Read the SQL file
    sql_file = os.path.join(os.path.dirname(__file__), 'create_insurance_tables_supabase.sql')
    with open(sql_file, 'r') as f:
        sql_content = f.read()
    
    try:
        # Execute the SQL
        result = sb.rpc('exec_sql', {'sql': sql_content})
        print("✅ Insurance tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        print("You may need to run the SQL manually in Supabase dashboard.")
        print(f"SQL file location: {sql_file}")
        return False

if __name__ == "__main__":
    setup_insurance_tables()