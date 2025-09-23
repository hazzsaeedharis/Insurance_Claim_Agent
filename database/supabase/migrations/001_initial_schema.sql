-- ClaimAI Pro Database Schema
-- Initial migration for insurance claims processing platform

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
CREATE TYPE claim_status AS ENUM (
    'submitted',
    'under_review', 
    'ai_processing',
    'approved',
    'rejected',
    'payment_pending',
    'completed'
);

CREATE TYPE user_role AS ENUM (
    'admin',
    'claims_processor',
    'claimant',
    'reviewer'
);

CREATE TYPE document_type AS ENUM (
    'claim_form',
    'incident_report',
    'photograph',
    'receipt',
    'police_report',
    'medical_report',
    'other'
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'claimant',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Claims table
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    claimant_name VARCHAR(255) NOT NULL,
    policy_number VARCHAR(100) NOT NULL,
    incident_date TIMESTAMP WITH TIME ZONE NOT NULL,
    claim_amount DECIMAL(12,2) NOT NULL,
    incident_type VARCHAR(100) NOT NULL,
    location TEXT,
    description TEXT,
    status claim_status DEFAULT 'submitted',
    ai_analysis JSONB,
    fraud_assessment JSONB,
    decision JSONB,
    reviewer_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID REFERENCES claims(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    document_type document_type NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_path TEXT,
    content BYTEA,
    processed BOOLEAN DEFAULT false,
    ai_analysis JSONB,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Policies table
CREATE TABLE policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    policy_number VARCHAR(100) UNIQUE NOT NULL,
    policy_type VARCHAR(50) NOT NULL,
    coverage_amount DECIMAL(12,2),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    claim_id UUID REFERENCES claims(id),
    action VARCHAR(100) NOT NULL,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI processing logs table
CREATE TABLE ai_processing_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID REFERENCES claims(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    model_version VARCHAR(100),
    processing_time DECIMAL(8,3),
    input_data JSONB,
    output_data JSONB,
    confidence_score DECIMAL(5,4),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_claims_user_id ON claims(user_id);
CREATE INDEX idx_claims_status ON claims(status);
CREATE INDEX idx_claims_created_at ON claims(created_at);
CREATE INDEX idx_documents_claim_id ON documents(claim_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_claim_id ON audit_logs(claim_id);
CREATE INDEX idx_ai_logs_claim_id ON ai_processing_logs(claim_id);

-- Row Level Security (RLS) policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_processing_logs ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Claims policies
CREATE POLICY "Users can view own claims" ON claims
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own claims" ON claims
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own claims" ON claims
    FOR UPDATE USING (auth.uid() = user_id);

-- Admin can see all claims
CREATE POLICY "Admins can view all claims" ON claims
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role IN ('admin', 'claims_processor', 'reviewer')
        )
    );

-- Documents policies
CREATE POLICY "Users can view claim documents" ON documents
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM claims 
            WHERE id = documents.claim_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can upload to own claims" ON documents
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM claims 
            WHERE id = documents.claim_id AND user_id = auth.uid()
        )
    );

-- Audit logs (admin only)
CREATE POLICY "Admins can view audit logs" ON audit_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Functions for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_claims_updated_at BEFORE UPDATE ON claims
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_policies_updated_at BEFORE UPDATE ON policies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for development
INSERT INTO users (email, full_name, role) VALUES
    ('admin@claimai-pro.com', 'Admin User', 'admin'),
    ('processor@claimai-pro.com', 'Claims Processor', 'claims_processor'),
    ('reviewer@claimai-pro.com', 'Reviewer', 'reviewer'),
    ('claimant@example.com', 'John Smith', 'claimant');

-- Insert sample policies
INSERT INTO policies (user_id, policy_number, policy_type, coverage_amount, start_date, end_date) 
SELECT 
    u.id,
    'POL-2024-' || LPAD(ROW_NUMBER() OVER()::text, 6, '0'),
    CASE (ROW_NUMBER() OVER() % 3)
        WHEN 0 THEN 'Auto'
        WHEN 1 THEN 'Home'
        ELSE 'Health'
    END,
    (50000 + (ROW_NUMBER() OVER() * 10000))::DECIMAL,
    CURRENT_DATE - INTERVAL '1 year',
    CURRENT_DATE + INTERVAL '1 year'
FROM users u 
WHERE u.role = 'claimant';

-- Insert sample claims
INSERT INTO claims (user_id, claimant_name, policy_number, incident_date, claim_amount, incident_type, location, description, status)
SELECT 
    u.id,
    u.full_name,
    p.policy_number,
    CURRENT_DATE - INTERVAL '7 days',
    (1000 + (ROW_NUMBER() OVER() * 500))::DECIMAL,
    CASE (ROW_NUMBER() OVER() % 4)
        WHEN 0 THEN 'Vehicle Collision'
        WHEN 1 THEN 'Property Damage'
        WHEN 2 THEN 'Medical Emergency'
        ELSE 'Theft'
    END,
    '123 Main St, Anytown, USA',
    'Sample claim description for testing purposes',
    CASE (ROW_NUMBER() OVER() % 3)
        WHEN 0 THEN 'submitted'
        WHEN 1 THEN 'under_review'
        ELSE 'approved'
    END::claim_status
FROM users u
JOIN policies p ON p.user_id = u.id
WHERE u.role = 'claimant'
LIMIT 5;
