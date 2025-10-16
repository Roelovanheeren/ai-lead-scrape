-- Enhanced Lead Generation Platform Database Schema
-- Builds upon existing lead schema with new capabilities

-- Core job management
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt TEXT NOT NULL,
    parameters JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    user_id UUID,
    vertical VARCHAR(100),
    target_count INTEGER DEFAULT 25,
    quality_threshold FLOAT DEFAULT 0.8
);

-- Enhanced company model
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    website VARCHAR(500),
    domain VARCHAR(255),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    industry VARCHAR(100),
    employee_count INTEGER,
    revenue_range VARCHAR(50),
    funding_stage VARCHAR(50),
    attributes JSONB,
    discovery_confidence FLOAT DEFAULT 0.0,
    fit_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contact discovery and verification
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    title VARCHAR(200),
    email VARCHAR(255),
    phone VARCHAR(50),
    linkedin_url VARCHAR(500),
    department VARCHAR(100),
    seniority_level VARCHAR(50),
    fit_score FLOAT DEFAULT 0.0,
    email_confidence FLOAT DEFAULT 0.0,
    email_status VARCHAR(50), -- valid, invalid, accept_all, unknown
    verification_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Deep research profiles
CREATE TABLE company_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    research_summary JSONB,
    pain_points JSONB,
    growth_signals JSONB,
    tech_stack JSONB,
    buying_triggers JSONB,
    recent_investments JSONB,
    reasons_to_reach_out JSONB,
    sources JSONB,
    research_confidence FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Outreach content generation
CREATE TABLE outreach_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(id) ON DELETE SET NULL,
    channel VARCHAR(50) NOT NULL, -- linkedin, email
    subject VARCHAR(500),
    body TEXT,
    tone VARCHAR(50) DEFAULT 'professional',
    word_count INTEGER,
    qa_feedback JSONB,
    quality_score FLOAT DEFAULT 0.0,
    status VARCHAR(50) DEFAULT 'draft', -- draft, approved, sent, failed
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quality assurance tracking
CREATE TABLE qa_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_type VARCHAR(50) NOT NULL, -- company, contact, outreach
    record_id UUID NOT NULL,
    reviewer_id UUID,
    status VARCHAR(50) NOT NULL, -- pending, approved, rejected, needs_revision
    feedback TEXT,
    score FLOAT,
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- API usage tracking
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    provider VARCHAR(100) NOT NULL,
    endpoint VARCHAR(200),
    request_count INTEGER DEFAULT 1,
    cost_usd DECIMAL(10,4) DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Outreach automation tracking
CREATE TABLE outreach_automation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outreach_id UUID REFERENCES outreach_content(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- aimfox, ghl, linkedin
    external_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    sent_at TIMESTAMPTZ,
    response_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_companies_job_id ON companies(job_id);
CREATE INDEX idx_companies_domain ON companies(domain);
CREATE INDEX idx_contacts_company_id ON contacts(company_id);
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_company_profiles_company_id ON company_profiles(company_id);
CREATE INDEX idx_outreach_content_company_id ON outreach_content(company_id);
CREATE INDEX idx_outreach_content_channel ON outreach_content(channel);
CREATE INDEX idx_qa_reviews_record ON qa_reviews(record_type, record_id);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_contacts_updated_at BEFORE UPDATE ON contacts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_company_profiles_updated_at BEFORE UPDATE ON company_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_outreach_content_updated_at BEFORE UPDATE ON outreach_content FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
