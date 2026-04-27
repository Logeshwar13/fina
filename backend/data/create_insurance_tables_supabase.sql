-- Create insurance_policies table
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

-- Create insurance_risk_assessments table
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_insurance_policies_user_id ON insurance_policies(user_id);
CREATE INDEX IF NOT EXISTS idx_insurance_policies_type ON insurance_policies(policy_type);
CREATE INDEX IF NOT EXISTS idx_insurance_policies_status ON insurance_policies(status);
CREATE INDEX IF NOT EXISTS idx_insurance_assessments_user_id ON insurance_risk_assessments(user_id);

-- Create updated_at trigger for insurance_policies
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_insurance_policies_updated_at 
    BEFORE UPDATE ON insurance_policies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_insurance_assessments_updated_at 
    BEFORE UPDATE ON insurance_risk_assessments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS (Row Level Security)
ALTER TABLE insurance_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE insurance_risk_assessments ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (users can only access their own data)
CREATE POLICY "Users can view their own insurance policies" ON insurance_policies
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert their own insurance policies" ON insurance_policies
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own insurance policies" ON insurance_policies
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete their own insurance policies" ON insurance_policies
    FOR DELETE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can view their own insurance assessments" ON insurance_risk_assessments
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can insert their own insurance assessments" ON insurance_risk_assessments
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own insurance assessments" ON insurance_risk_assessments
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete their own insurance assessments" ON insurance_risk_assessments
    FOR DELETE USING (auth.uid()::text = user_id::text);