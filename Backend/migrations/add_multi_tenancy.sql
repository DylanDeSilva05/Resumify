-- Migration Script: Add Multi-Tenancy Support
-- Description: Adds company_id to all tables and creates Company table
-- Date: 2025-10-07
-- IMPORTANT: Backup your database before running this migration!

-- ============================================================
-- STEP 1: Create Companies Table
-- ============================================================

CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR UNIQUE NOT NULL,
    contact_email VARCHAR NOT NULL,
    contact_phone VARCHAR,
    address TEXT,
    city VARCHAR,
    state VARCHAR,
    country VARCHAR,
    postal_code VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    subscription_tier VARCHAR DEFAULT 'basic',
    max_users INTEGER DEFAULT 5,
    max_cv_uploads_monthly INTEGER DEFAULT 100,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_companies_company_name ON companies(company_name);
CREATE INDEX idx_companies_contact_email ON companies(contact_email);

-- ============================================================
-- STEP 2: Create a Default Company for Existing Data
-- ============================================================

-- Insert a default company for existing records
INSERT INTO companies (company_name, contact_email, is_active, subscription_tier, max_users)
VALUES ('Default Company', 'admin@resumify.com', TRUE, 'enterprise', 999)
ON CONFLICT (company_name) DO NOTHING;

-- ============================================================
-- STEP 3: Add company_id to Users Table
-- ============================================================

-- Add company_id column (nullable initially for existing users)
ALTER TABLE users ADD COLUMN IF NOT EXISTS company_id INTEGER;

-- Add role column (new role-based system)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
        CREATE TYPE userrole AS ENUM ('super_admin', 'company_admin', 'company_user', 'recruiter');
    END IF;
END $$;

ALTER TABLE users ADD COLUMN IF NOT EXISTS role userrole DEFAULT 'company_user';

-- Set default company for existing users
UPDATE users
SET company_id = (SELECT id FROM companies WHERE company_name = 'Default Company' LIMIT 1)
WHERE company_id IS NULL;

-- Add foreign key constraint
ALTER TABLE users
ADD CONSTRAINT fk_users_company
FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_users_company_id ON users(company_id);

-- ============================================================
-- STEP 4: Add company_id to Candidates Table
-- ============================================================

ALTER TABLE candidates ADD COLUMN IF NOT EXISTS company_id INTEGER;

-- Set default company for existing candidates
UPDATE candidates
SET company_id = (SELECT id FROM companies WHERE company_name = 'Default Company' LIMIT 1)
WHERE company_id IS NULL;

-- Make company_id required and add foreign key
ALTER TABLE candidates ALTER COLUMN company_id SET NOT NULL;
ALTER TABLE candidates
ADD CONSTRAINT fk_candidates_company
FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_candidates_company_id ON candidates(company_id);

-- ============================================================
-- STEP 5: Add company_id to Job Postings Table
-- ============================================================

ALTER TABLE job_postings ADD COLUMN IF NOT EXISTS company_id INTEGER;

-- Set default company for existing job postings
UPDATE job_postings
SET company_id = (SELECT id FROM companies WHERE company_name = 'Default Company' LIMIT 1)
WHERE company_id IS NULL;

-- Make company_id required and add foreign key
ALTER TABLE job_postings ALTER COLUMN company_id SET NOT NULL;
ALTER TABLE job_postings
ADD CONSTRAINT fk_job_postings_company
FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_job_postings_company_id ON job_postings(company_id);

-- ============================================================
-- STEP 6: Add company_id to CV Analyses Table
-- ============================================================

ALTER TABLE cv_analyses ADD COLUMN IF NOT EXISTS company_id INTEGER;

-- Set default company for existing analyses
UPDATE cv_analyses
SET company_id = (SELECT id FROM companies WHERE company_name = 'Default Company' LIMIT 1)
WHERE company_id IS NULL;

-- Make company_id required and add foreign key
ALTER TABLE cv_analyses ALTER COLUMN company_id SET NOT NULL;
ALTER TABLE cv_analyses
ADD CONSTRAINT fk_cv_analyses_company
FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_cv_analyses_company_id ON cv_analyses(company_id);

-- ============================================================
-- STEP 7: Add company_id to Interviews Table
-- ============================================================

ALTER TABLE interviews ADD COLUMN IF NOT EXISTS company_id INTEGER;

-- Set default company for existing interviews
UPDATE interviews
SET company_id = (SELECT id FROM companies WHERE company_name = 'Default Company' LIMIT 1)
WHERE company_id IS NULL;

-- Make company_id required and add foreign key
ALTER TABLE interviews ALTER COLUMN company_id SET NOT NULL;
ALTER TABLE interviews
ADD CONSTRAINT fk_interviews_company
FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_interviews_company_id ON interviews(company_id);

-- ============================================================
-- STEP 8: Update First User to be Super Admin
-- ============================================================

-- Make the first user a SUPER_ADMIN (adjust this based on your admin user)
UPDATE users
SET role = 'super_admin'::userrole,
    company_id = NULL  -- Super admins don't belong to any company
WHERE id = 1;

-- ============================================================
-- MIGRATION COMPLETE
-- ============================================================

-- Verify migration
SELECT 'Migration completed successfully!' AS status;
SELECT COUNT(*) AS total_companies FROM companies;
SELECT COUNT(*) AS users_with_company FROM users WHERE company_id IS NOT NULL;
SELECT COUNT(*) AS candidates_with_company FROM candidates WHERE company_id IS NOT NULL;
