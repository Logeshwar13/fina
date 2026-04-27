"""
data/create_rls_policies.py
───────────────────────────
Prints SQL to add permissive RLS policies for development.
Run the output in Supabase SQL Editor.
"""
SQL = """
-- Development: allow all operations for anon role on all tables
-- (In production, replace these with user-specific policies)

-- users
CREATE POLICY "anon_all_users"
  ON users FOR ALL
  TO anon
  USING (true)
  WITH CHECK (true);

-- transactions
CREATE POLICY "anon_all_transactions"
  ON transactions FOR ALL
  TO anon
  USING (true)
  WITH CHECK (true);

-- budgets
CREATE POLICY "anon_all_budgets"
  ON budgets FOR ALL
  TO anon
  USING (true)
  WITH CHECK (true);

-- risk_scores
CREATE POLICY "anon_all_risk_scores"
  ON risk_scores FOR ALL
  TO anon
  USING (true)
  WITH CHECK (true);
"""
print(SQL)
