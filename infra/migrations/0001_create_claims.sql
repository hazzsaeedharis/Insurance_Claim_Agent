-- 0001_create_claims.sql
-- Create claims table for insurance claim processing

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS claims (
    claim_id VARCHAR(12) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    policy_number VARCHAR(50),
    claim_type VARCHAR(20) CHECK (claim_type IN ('outpatient', 'inpatient', 'dental', 'vision', 'pharmacy', 'emergency')),
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'under_review', 'approved', 'rejected', 'paid', 'appealed', 'closed')),
    total_amount DECIMAL(10, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'EUR',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE,
    adjuster_id VARCHAR(50),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes
CREATE INDEX idx_claims_customer_id ON claims(customer_id);
CREATE INDEX idx_claims_status ON claims(status);
CREATE INDEX idx_claims_claim_type ON claims(claim_type);
CREATE INDEX idx_claims_created_at ON claims(created_at);
CREATE INDEX idx_claims_adjuster_id ON claims(adjuster_id);

-- Create claim_items table
CREATE TABLE IF NOT EXISTS claim_items (
    item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id VARCHAR(12) REFERENCES claims(claim_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    provider VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    description TEXT,
    quantity DECIMAL(10, 2) DEFAULT 1,
    net_amount DECIMAL(10, 2) NOT NULL,
    gross_amount DECIMAL(10, 2),
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    covered_amount DECIMAL(10, 2) DEFAULT 0,
    deductible_applied DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for claim_items
CREATE INDEX idx_claim_items_claim_id ON claim_items(claim_id);
CREATE INDEX idx_claim_items_date ON claim_items(date);
CREATE INDEX idx_claim_items_provider ON claim_items(provider);

-- Create claim_notes table
CREATE TABLE IF NOT EXISTS claim_notes (
    note_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id VARCHAR(12) REFERENCES claims(claim_id) ON DELETE CASCADE,
    author_id VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    visibility VARCHAR(20) DEFAULT 'internal' CHECK (visibility IN ('internal', 'customer', 'all')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for claim_notes
CREATE INDEX idx_claim_notes_claim_id ON claim_notes(claim_id);
CREATE INDEX idx_claim_notes_author_id ON claim_notes(author_id);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_claims_updated_at BEFORE UPDATE
    ON claims FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE claims IS 'Main table storing insurance claims';
COMMENT ON COLUMN claims.claim_id IS 'Unique claim identifier in format CLM-XXXXXXXX';
COMMENT ON COLUMN claims.metadata IS 'Additional metadata including fraud_score, auto_approved, processing_time_seconds';

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE ON claims TO insurance_api_user;
-- GRANT SELECT, INSERT ON claim_items TO insurance_api_user;
-- GRANT SELECT, INSERT ON claim_notes TO insurance_api_user;