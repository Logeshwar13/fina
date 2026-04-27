-- FinA Personal Finance Management System
-- Complete Database Schema for Supabase PostgreSQL
-- Run this in: Supabase Dashboard → SQL Editor → New Query

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    income DECIMAL(15,2) DEFAULT 0,
    goals_json JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(15,2) NOT NULL,
    description TEXT DEFAULT '',
    category TEXT DEFAULT 'Uncategorized',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    location TEXT DEFAULT '',
    type TEXT DEFAULT 'expense', -- expense | income
    is_fraud BOOLEAN DEFAULT FALSE,
    fraud_score DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Budgets table
CREATE TABLE IF NOT EXISTS budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    limit_amount DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Risk scores table
CREATE TABLE IF NOT EXISTS risk_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score INTEGER DEFAULT 50 CHECK (score >= 0 AND score <= 100),
    grade TEXT DEFAULT 'C',
    label TEXT DEFAULT 'Moderate Risk',
    breakdown_json JSONB DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INSURANCE TABLES
-- ============================================================================

-- Insurance policies table
CREATE TABLE IF NOT EXISTS insurance_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    policy_type VARCHAR(50) NOT NULL, -- health | life | vehicle | home | travel
    provider VARCHAR(200) DEFAULT '',
    policy_number VARCHAR(100) DEFAULT '',
    coverage_amount DECIMAL(15,2) NOT NULL,
    premium_amount DECIMAL(15,2) NOT NULL,
    premium_frequency VARCHAR(20) DEFAULT 'annual', -- annual | monthly | quarterly
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    beneficiaries JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(20) DEFAULT 'active', -- active | expired | cancelled
    notes TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insurance risk assessments table
CREATE TABLE IF NOT EXISTS insurance_risk_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    age INTEGER NOT NULL CHECK (age > 0 AND age < 120),
    dependents INTEGER DEFAULT 0 CHECK (dependents >= 0),
    annual_income DECIMAL(15,2) NOT NULL CHECK (annual_income > 0),
    monthly_expenses DECIMAL(15,2) NOT NULL CHECK (monthly_expenses > 0),
    existing_loans DECIMAL(15,2) DEFAULT 0.0 CHECK (existing_loans >= 0),
    health_conditions JSONB DEFAULT '[]'::jsonb,
    lifestyle_factors JSONB DEFAULT '{}'::jsonb,
    
    -- Calculated fields
    recommended_life_coverage DECIMAL(15,2) DEFAULT 0.0,
    recommended_health_coverage DECIMAL(15,2) DEFAULT 0.0,
    current_life_coverage DECIMAL(15,2) DEFAULT 0.0,
    current_health_coverage DECIMAL(15,2) DEFAULT 0.0,
    coverage_gap_life DECIMAL(15,2) DEFAULT 0.0,
    coverage_gap_health DECIMAL(15,2) DEFAULT 0.0,
    risk_score INTEGER DEFAULT 50 CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_level VARCHAR(20) DEFAULT 'moderate', -- low | moderate | high
    recommendations JSONB DEFAULT '[]'::jsonb,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Transactions indexes
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_transactions_is_fraud ON transactions(is_fraud);

-- Budgets indexes
CREATE INDEX IF NOT EXISTS idx_budgets_user_id ON budgets(user_id);
CREATE INDEX IF NOT EXISTS idx_budgets_category ON budgets(category);

-- Risk scores indexes
CREATE INDEX IF NOT EXISTS idx_risk_scores_user_id ON risk_scores(user_id);

-- Insurance policies indexes
CREATE INDEX IF NOT EXISTS idx_insurance_policies_user_id ON insurance_policies(user_id);
CREATE INDEX IF NOT EXISTS idx_insurance_policies_type ON insurance_policies(policy_type);
CREATE INDEX IF NOT EXISTS idx_insurance_policies_status ON insurance_policies(status);
CREATE INDEX IF NOT EXISTS idx_insurance_policies_end_date ON insurance_policies(end_date);

-- Insurance assessments indexes
CREATE INDEX IF NOT EXISTS idx_insurance_assessments_user_id ON insurance_risk_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_insurance_assessments_risk_level ON insurance_risk_assessments(risk_level);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_budgets_updated_at 
    BEFORE UPDATE ON budgets 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_risk_scores_updated_at 
    BEFORE UPDATE ON risk_scores 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_insurance_policies_updated_at 
    BEFORE UPDATE ON insurance_policies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_insurance_assessments_updated_at 
    BEFORE UPDATE ON insurance_risk_assessments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE budgets ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE insurance_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE insurance_risk_assessments ENABLE ROW LEVEL SECURITY;

-- Users policies
CREATE POLICY "Users can view their own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Transactions policies
CREATE POLICY "Users can view their own transactions" ON transactions
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert their own transactions" ON transactions
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own transactions" ON transactions
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete their own transactions" ON transactions
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- Budgets policies
CREATE POLICY "Users can view their own budgets" ON budgets
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert their own budgets" ON budgets
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own budgets" ON budgets
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete their own budgets" ON budgets
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- Risk scores policies
CREATE POLICY "Users can view their own risk scores" ON risk_scores
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert their own risk scores" ON risk_scores
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own risk scores" ON risk_scores
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- Insurance policies policies
CREATE POLICY "Users can view their own insurance policies" ON insurance_policies
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert their own insurance policies" ON insurance_policies
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own insurance policies" ON insurance_policies
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete their own insurance policies" ON insurance_policies
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- Insurance assessments policies
CREATE POLICY "Users can view their own insurance assessments" ON insurance_risk_assessments
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert their own insurance assessments" ON insurance_risk_assessments
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own insurance assessments" ON insurance_risk_assessments
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete their own insurance assessments" ON insurance_risk_assessments
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- ============================================================================
-- SAMPLE DATA (OPTIONAL - FOR TESTING)
-- ============================================================================

-- Uncomment to insert sample data for testing

/*
-- Insert sample user
INSERT INTO users (id, name, email, income) VALUES
('ad200e5a-3d99-4d9f-850b-22ae2563bcc4', 'Test User', 'test@example.com', 1200000);

-- Insert sample transactions
INSERT INTO transactions (user_id, amount, description, category, type) VALUES
('ad200e5a-3d99-4d9f-850b-22ae2563bcc4', 500, 'Grocery shopping', 'Food & Dining', 'expense'),
('ad200e5a-3d99-4d9f-850b-22ae2563bcc4', 50000, 'Monthly salary', 'Income', 'income');

-- Insert sample budgets
INSERT INTO budgets (user_id, category, limit_amount) VALUES
('ad200e5a-3d99-4d9f-850b-22ae2563bcc4', 'Food & Dining', 15000),
('ad200e5a-3d99-4d9f-850b-22ae2563bcc4', 'Transportation', 5000);
*/

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'transactions', 'budgets', 'risk_scores', 'insurance_policies', 'insurance_risk_assessments')
ORDER BY table_name;

-- Check indexes
SELECT tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'transactions', 'budgets', 'risk_scores', 'insurance_policies', 'insurance_risk_assessments')
ORDER BY tablename, indexname;

-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'transactions', 'budgets', 'risk_scores', 'insurance_policies', 'insurance_risk_assessments')
ORDER BY tablename;

-- ============================================================================
-- NOTES
-- ============================================================================

/*
This schema creates all tables needed for the FinA Personal Finance Management System:

1. CORE TABLES:
   - users: User profiles and income information
   - transactions: Financial transactions (income/expense)
   - budgets: Budget limits by category
   - risk_scores: Financial health risk assessments

2. INSURANCE TABLES:
   - insurance_policies: User insurance policies
   - insurance_risk_assessments: Insurance needs assessments

3. FEATURES:
   - UUID primary keys for all tables
   - Foreign key constraints with CASCADE delete
   - Indexes for query performance
   - Automatic updated_at timestamps
   - Row Level Security (RLS) enabled
   - RLS policies for user data isolation
   - JSONB fields for flexible data storage
   - Check constraints for data validation

4. SECURITY:
   - RLS ensures users can only access their own data
   - Policies use auth.uid() for authentication
   - All sensitive operations are protected

5. PERFORMANCE:
   - Indexes on frequently queried columns
   - JSONB for flexible schema evolution
   - Efficient foreign key relationships

To use this schema:
1. Go to Supabase Dashboard → SQL Editor
2. Create a new query
3. Paste this entire file
4. Click "Run"
5. Verify tables are created using the verification queries at the end

For development/testing, you can disable RLS temporarily:
ALTER TABLE table_name DISABLE ROW LEVEL SECURITY;

Remember to re-enable RLS before production deployment!
*/
