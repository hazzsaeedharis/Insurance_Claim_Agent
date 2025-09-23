-- ClaimAI Pro Database Schema
-- This creates the complete database structure for our insurance claims processing platform

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create custom types
CREATE TYPE user_role AS ENUM ('claimant', 'adjuster', 'admin', 'manager');
CREATE TYPE claim_status AS ENUM ('submitted', 'processing', 'under_review', 'approved', 'rejected', 'paid');
CREATE TYPE claim_type AS ENUM ('auto', 'property', 'health', 'liability', 'workers_comp');
CREATE TYPE document_type AS ENUM ('photo', 'receipt', 'police_report', 'medical_record', 'estimate', 'other');
CREATE TYPE processing_step AS ENUM ('document_extraction', 'fraud_detection', 'policy_verification', 'damage_assessment', 'final_review');

-- Users table (extends Supabase auth.users)
CREATE TABLE public.profiles (
    id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    role user_role DEFAULT 'claimant',
    company_name TEXT,
    phone TEXT,
    address JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Insurance policies table
CREATE TABLE public.policies (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    policy_number TEXT UNIQUE NOT NULL,
    holder_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    policy_type claim_type NOT NULL,
    coverage_details JSONB NOT NULL, -- Coverage limits, deductibles, etc.
    premium_amount DECIMAL(10,2),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Claims table
CREATE TABLE public.claims (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    claim_number TEXT UNIQUE NOT NULL,
    claimant_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    policy_id UUID REFERENCES public.policies(id) ON DELETE RESTRICT,
    claim_type claim_type NOT NULL,
    status claim_status DEFAULT 'submitted',
    
    -- Incident details
    incident_date TIMESTAMP WITH TIME ZONE NOT NULL,
    incident_location TEXT,
    incident_description TEXT NOT NULL,
    estimated_amount DECIMAL(10,2),
    final_amount DECIMAL(10,2),
    
    -- AI processing metadata
    ai_confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    fraud_risk_score DECIMAL(3,2), -- 0.00 to 1.00
    processing_notes TEXT,
    
    -- Assignment
    assigned_adjuster_id UUID REFERENCES public.profiles(id),
    
    -- Timestamps
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Documents table
CREATE TABLE public.claim_documents (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    claim_id UUID REFERENCES public.claims(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    file_type document_type NOT NULL,
    mime_type TEXT,
    
    -- AI processing results
    extracted_text TEXT,
    extracted_data JSONB, -- Structured data extracted by AI
    processing_confidence DECIMAL(3,2),
    ocr_confidence DECIMAL(3,2),
    
    uploaded_by UUID REFERENCES public.profiles(id),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- AI processing log for audit trail
CREATE TABLE public.ai_processing_log (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    claim_id UUID REFERENCES public.claims(id) ON DELETE CASCADE,
    processing_step processing_step NOT NULL,
    
    -- Input/Output data
    input_data JSONB,
    output_data JSONB,
    confidence_score DECIMAL(3,2),
    
    -- Performance metrics
    processing_time_ms INTEGER,
    model_used TEXT,
    
    -- Error handling
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Claim status history for tracking
CREATE TABLE public.claim_status_history (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    claim_id UUID REFERENCES public.claims(id) ON DELETE CASCADE,
    old_status claim_status,
    new_status claim_status NOT NULL,
    changed_by UUID REFERENCES public.profiles(id),
    reason TEXT,
    notes TEXT,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Notifications table
CREATE TABLE public.notifications (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    claim_id UUID REFERENCES public.claims(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT DEFAULT 'info', -- 'info', 'success', 'warning', 'error'
    read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Fraud patterns table for machine learning
CREATE TABLE public.fraud_patterns (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    pattern_type TEXT NOT NULL,
    pattern_data JSONB NOT NULL,
    confidence_threshold DECIMAL(3,2) DEFAULT 0.7,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Create indexes for performance
CREATE INDEX idx_claims_claimant_id ON public.claims(claimant_id);
CREATE INDEX idx_claims_status ON public.claims(status);
CREATE INDEX idx_claims_claim_type ON public.claims(claim_type);
CREATE INDEX idx_claims_assigned_adjuster ON public.claims(assigned_adjuster_id);
CREATE INDEX idx_claims_submitted_at ON public.claims(submitted_at);
CREATE INDEX idx_claim_documents_claim_id ON public.claim_documents(claim_id);
CREATE INDEX idx_ai_processing_log_claim_id ON public.ai_processing_log(claim_id);
CREATE INDEX idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX idx_notifications_unread ON public.notifications(user_id, read) WHERE read = false;

-- Row Level Security (RLS) Policies

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.claim_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_processing_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.claim_status_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- Claims policies
CREATE POLICY "Claimants can view own claims" ON public.claims
    FOR SELECT USING (claimant_id = auth.uid());

CREATE POLICY "Adjusters can view assigned claims" ON public.claims
    FOR SELECT USING (
        assigned_adjuster_id = auth.uid() OR
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = auth.uid() 
            AND role IN ('adjuster', 'admin', 'manager')
        )
    );

CREATE POLICY "Claimants can create claims" ON public.claims
    FOR INSERT WITH CHECK (claimant_id = auth.uid());

CREATE POLICY "Adjusters can update claims" ON public.claims
    FOR UPDATE USING (
        assigned_adjuster_id = auth.uid() OR
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = auth.uid() 
            AND role IN ('adjuster', 'admin', 'manager')
        )
    );

-- Documents policies
CREATE POLICY "Users can view documents for their claims" ON public.claim_documents
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.claims 
            WHERE id = claim_id 
            AND (claimant_id = auth.uid() OR assigned_adjuster_id = auth.uid())
        ) OR
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = auth.uid() 
            AND role IN ('adjuster', 'admin', 'manager')
        )
    );

CREATE POLICY "Users can upload documents to their claims" ON public.claim_documents
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.claims 
            WHERE id = claim_id 
            AND claimant_id = auth.uid()
        ) OR
        uploaded_by = auth.uid()
    );

-- Notifications policies
CREATE POLICY "Users can view own notifications" ON public.notifications
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can update own notifications" ON public.notifications
    FOR UPDATE USING (user_id = auth.uid());

-- Functions for automatic updates
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER handle_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_policies_updated_at
    BEFORE UPDATE ON public.policies
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_claims_updated_at
    BEFORE UPDATE ON public.claims
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- Function to generate claim numbers
CREATE OR REPLACE FUNCTION public.generate_claim_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.claim_number = 'CLM-' || TO_CHAR(NOW(), 'YYYY') || '-' || LPAD(NEXTVAL('claim_number_seq')::TEXT, 6, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create sequence for claim numbers
CREATE SEQUENCE claim_number_seq START 1;

-- Create trigger for claim number generation
CREATE TRIGGER generate_claim_number_trigger
    BEFORE INSERT ON public.claims
    FOR EACH ROW
    EXECUTE FUNCTION public.generate_claim_number();

-- Function to log status changes
CREATE OR REPLACE FUNCTION public.log_claim_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO public.claim_status_history (claim_id, old_status, new_status, changed_by)
        VALUES (NEW.id, OLD.status, NEW.status, auth.uid());
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for status change logging
CREATE TRIGGER log_claim_status_change_trigger
    AFTER UPDATE ON public.claims
    FOR EACH ROW
    EXECUTE FUNCTION public.log_claim_status_change();

-- Insert sample fraud patterns
INSERT INTO public.fraud_patterns (pattern_type, pattern_data, confidence_threshold) VALUES
('duplicate_claim', '{"description": "Multiple claims for same incident", "indicators": ["same_date", "same_location", "similar_amount"]}', 0.8),
('excessive_amount', '{"description": "Claim amount significantly higher than average", "indicators": ["amount_deviation", "policy_limits"]}', 0.7),
('rapid_submission', '{"description": "Multiple claims submitted in short timeframe", "indicators": ["submission_frequency", "time_gaps"]}', 0.6);

-- Create view for claim summary
CREATE VIEW public.claim_summary AS
SELECT 
    c.id,
    c.claim_number,
    c.claim_type,
    c.status,
    c.estimated_amount,
    c.final_amount,
    c.incident_date,
    c.submitted_at,
    p.full_name as claimant_name,
    p.email as claimant_email,
    adj.full_name as adjuster_name,
    pol.policy_number,
    COUNT(cd.id) as document_count
FROM public.claims c
LEFT JOIN public.profiles p ON c.claimant_id = p.id
LEFT JOIN public.profiles adj ON c.assigned_adjuster_id = adj.id
LEFT JOIN public.policies pol ON c.policy_id = pol.id
LEFT JOIN public.claim_documents cd ON c.id = cd.claim_id
GROUP BY c.id, p.full_name, p.email, adj.full_name, pol.policy_number;
