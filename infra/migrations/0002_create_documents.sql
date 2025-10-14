-- 0002_create_documents.sql
-- Create documents table for claim attachments

CREATE TABLE IF NOT EXISTS documents (
    document_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id VARCHAR(12) REFERENCES claims(claim_id) ON DELETE CASCADE,
    document_type VARCHAR(20) NOT NULL CHECK (document_type IN ('receipt', 'prescription', 'referral', 'medical_report', 'invoice', 'other')),
    filename VARCHAR(255) NOT NULL,
    storage_key VARCHAR(500) NOT NULL UNIQUE,
    checksum VARCHAR(64),
    size_bytes BIGINT,
    mimetype VARCHAR(100),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    uploaded_by VARCHAR(50) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP WITH TIME ZONE,
    verified_by VARCHAR(50),
    ocr_text TEXT,
    ocr_confidence DECIMAL(3, 2),
    ocr_processed_at TIMESTAMP WITH TIME ZONE,
    language VARCHAR(5),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes
CREATE INDEX idx_documents_claim_id ON documents(claim_id);
CREATE INDEX idx_documents_document_type ON documents(document_type);
CREATE INDEX idx_documents_uploaded_at ON documents(uploaded_at);
CREATE INDEX idx_documents_verified ON documents(verified);
CREATE INDEX idx_documents_storage_key ON documents(storage_key);

-- Create document_pages table for multi-page documents
CREATE TABLE IF NOT EXISTS document_pages (
    page_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(document_id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    ocr_text TEXT,
    ocr_confidence DECIMAL(3, 2),
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(document_id, page_number)
);

-- Create index for document_pages
CREATE INDEX idx_document_pages_document_id ON document_pages(document_id);

-- Create audit log table for document operations
CREATE TABLE IF NOT EXISTS document_audit (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(document_id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,
    performed_by VARCHAR(50) NOT NULL,
    performed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    details JSONB DEFAULT '{}'::jsonb
);

-- Create index for document_audit
CREATE INDEX idx_document_audit_document_id ON document_audit(document_id);
CREATE INDEX idx_document_audit_performed_at ON document_audit(performed_at);

-- Comments
COMMENT ON TABLE documents IS 'Stores metadata for all claim-related documents';
COMMENT ON COLUMN documents.storage_key IS 'S3/MinIO object key for document storage';
COMMENT ON COLUMN documents.checksum IS 'SHA256 hash of document for integrity verification';
COMMENT ON COLUMN documents.ocr_text IS 'Extracted text from OCR processing';
COMMENT ON COLUMN documents.ocr_confidence IS 'OCR confidence score (0-1)';

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE ON documents TO insurance_api_user;
-- GRANT SELECT, INSERT ON document_pages TO insurance_api_user;
-- GRANT SELECT, INSERT ON document_audit TO insurance_api_user;