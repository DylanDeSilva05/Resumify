# Multi-Tenancy Implementation Guide

## Overview

Resumify now supports **multi-tenant architecture** with complete data isolation between companies. This ensures that:
- Company A cannot see Company B's candidates, CVs, or job postings
- Each company's data is completely isolated
- Super admins can manage multiple companies
- Company admins can manage their own company users

---

## Architecture Changes

### 1. New Role Hierarchy

```python
class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"      # System owner - can create companies
    COMPANY_ADMIN = "company_admin"  # Company owner - can manage company users
    COMPANY_USER = "company_user"    # Regular employee - can use features
    RECRUITER = "recruiter"          # Limited access - CV screening only
```

**Role Permissions:**

| Role | Create Companies | Manage Own Company | Create Users | Upload CVs | View Other Companies |
|------|-----------------|-------------------|--------------|-----------|---------------------|
| SUPER_ADMIN | ✅ | ✅ | ✅ | ✅ | ✅ |
| COMPANY_ADMIN | ❌ | ✅ | ✅ (own company) | ✅ | ❌ |
| COMPANY_USER | ❌ | ❌ | ❌ | ✅ | ❌ |
| RECRUITER | ❌ | ❌ | ❌ | ✅ (limited) | ❌ |

### 2. New Database Schema

#### Companies Table
```sql
CREATE TABLE companies (
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
```

#### Modified Tables
All data tables now include `company_id`:
- `users.company_id` (nullable for SUPER_ADMIN)
- `candidates.company_id` (required)
- `job_postings.company_id` (required)
- `cv_analyses.company_id` (required)
- `interviews.company_id` (required)

---

## Migration Steps

### Step 1: Backup Database

⚠️ **CRITICAL: Backup your database before proceeding!**

```bash
# PostgreSQL backup
pg_dump -U your_username -d resumify > backup_before_migration.sql
```

### Step 2: Run Migration Script

```bash
# From Backend directory
psql -U your_username -d resumify -f migrations/add_multi_tenancy.sql
```

This will:
1. Create the `companies` table
2. Add `company_id` to all tables
3. Create a "Default Company" for existing data
4. Migrate all existing data to the default company
5. Set up foreign key constraints

### Step 3: Verify Migration

```sql
-- Check companies
SELECT * FROM companies;

-- Verify all users have company_id
SELECT COUNT(*) FROM users WHERE company_id IS NULL AND role != 'super_admin';
-- Should return 0

-- Verify all candidates have company_id
SELECT COUNT(*) FROM candidates WHERE company_id IS NULL;
-- Should return 0
```

### Step 4: Make Yourself Super Admin

```sql
UPDATE users
SET role = 'super_admin'::userrole,
    company_id = NULL
WHERE email = 'your_admin@email.com';
```

### Step 5: Restart Backend Application

```bash
cd Backend
# Restart your server (e.g., uvicorn, gunicorn, etc.)
```

---

## API Changes

### New Endpoints

#### Company Management (Super Admin Only)

```http
POST /api/v1/companies/
GET /api/v1/companies/
GET /api/v1/companies/{company_id}
PUT /api/v1/companies/{company_id}
DELETE /api/v1/companies/{company_id}
GET /api/v1/companies/{company_id}/stats
```

#### My Company (All Users)

```http
GET /api/v1/companies/my-company
```

### Modified Endpoints

All data endpoints now filter by `company_id`:

```python
# Before (NO FILTERING - INSECURE!)
query = db.query(Candidate)

# After (FILTERED BY COMPANY)
query = db.query(Candidate)
if current_user.company_id:
    query = query.filter(Candidate.company_id == current_user.company_id)
```

**Affected Endpoints:**
- `GET /api/v1/candidates/` - Only returns user's company candidates
- `GET /api/v1/candidates/{id}` - Only if candidate belongs to user's company
- `POST /api/v1/analysis/upload-and-analyze` - Sets company_id automatically
- `GET /api/v1/analysis/results/{id}` - Only if analysis belongs to user's company
- `GET /api/v1/analysis/candidates/{status}` - Filtered by company

---

## Workflow Examples

### 1. Super Admin Creates New Company

```python
import requests

# Login as super admin
response = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'username': 'admin',
    'password': 'your_password'
})
token = response.json()['access_token']

# Create new company
response = requests.post(
    'http://localhost:8000/api/v1/companies/',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'company_name': 'ABC Corporation',
        'contact_email': 'contact@abc.com',
        'contact_phone': '+1234567890',
        'subscription_tier': 'premium',
        'max_users': 20
    }
)

company = response.json()
print(f"Created company: {company['company_name']} (ID: {company['id']})")
```

### 2. Super Admin Creates Company Admin User

```python
# Create user for the company
response = requests.post(
    'http://localhost:8000/api/v1/users/',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'username': 'abc_admin',
        'email': 'admin@abc.com',
        'full_name': 'ABC Admin',
        'password': 'secure_password',
        'company_id': company['id'],  # Link to company
        'role': 'company_admin'
    }
)
```

### 3. Company Admin Creates Employee User

```python
# Login as company admin
response = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'username': 'abc_admin',
    'password': 'secure_password'
})
admin_token = response.json()['access_token']

# Create employee (company_id inherited automatically)
response = requests.post(
    'http://localhost:8000/api/v1/users/',
    headers={'Authorization': f'Bearer {admin_token}'},
    json={
        'username': 'john_recruiter',
        'email': 'john@abc.com',
        'full_name': 'John Recruiter',
        'password': 'password123',
        'role': 'recruiter'
    }
)
```

### 4. Company User Uploads CVs

```python
# Login as company user
response = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'username': 'john_recruiter',
    'password': 'password123'
})
user_token = response.json()['access_token']

# Upload CVs (company_id set automatically)
files = [
    ('files', open('cv1.pdf', 'rb')),
    ('files', open('cv2.pdf', 'rb'))
]

response = requests.post(
    'http://localhost:8000/api/v1/analysis/upload-and-analyze',
    headers={'Authorization': f'Bearer {user_token}'},
    files=files,
    data={
        'job_title': 'Software Engineer',
        'job_requirements': 'Looking for Python developer...'
    }
)

# All candidates are automatically assigned to ABC Corporation
# Other companies CANNOT see these candidates
```

---

## Data Isolation Guarantees

### ✅ What's Protected

1. **Candidates** - Company A cannot see Company B's candidates
2. **Job Postings** - Each company's job postings are private
3. **CV Analyses** - Analysis results are company-scoped
4. **Interviews** - Interview schedules are company-private
5. **Users** - Super admins can see all, others only see their company

### ✅ Security Checks

Every API endpoint performs:
```python
# Automatic company filter
if current_user.company_id:
    query = query.filter(Model.company_id == current_user.company_id)
```

This ensures:
- Users can only access their company's data
- Database queries are automatically filtered
- No cross-company data leakage

### ✅ Cascade Deletion

When a company is deleted:
```sql
ON DELETE CASCADE
```
- All company users are deleted
- All company candidates are deleted
- All company job postings are deleted
- All company analyses are deleted
- All company interviews are deleted

---

## Testing Multi-Tenancy

### Test 1: Data Isolation

```python
# Create two companies
company_a = create_company('Company A', 'a@test.com')
company_b = create_company('Company B', 'b@test.com')

# Create users
user_a = create_user('user_a', company_a.id)
user_b = create_user('user_b', company_b.id)

# User A uploads candidate
candidate_a = upload_candidate(user_a, 'candidate_a.pdf')

# User B tries to access User A's candidate
response = get_candidate(user_b, candidate_a.id)
# Should return 404 NOT FOUND ✅

# User B lists all candidates
candidates = list_candidates(user_b)
# Should return empty list (no access to Company A's candidates) ✅
```

### Test 2: Super Admin Access

```python
# Super admin can see all companies
companies = list_companies(super_admin)
# Returns: [Company A, Company B] ✅

# Super admin can view any company's data
candidates_a = list_candidates(super_admin, company_id=company_a.id)
candidates_b = list_candidates(super_admin, company_id=company_b.id)
# Both succeed ✅
```

### Test 3: Role Permissions

```python
# Company admin tries to create another company
response = create_company(company_admin, 'New Company')
# Should return 403 FORBIDDEN ✅

# Company user tries to create another user
response = create_user(company_user, 'new_user')
# Should return 403 FORBIDDEN ✅
```

---

## Troubleshooting

### Issue: "User must be associated with a company"

**Solution:** Make sure the user has a `company_id`:
```sql
UPDATE users SET company_id = 1 WHERE id = YOUR_USER_ID;
```

### Issue: "Candidate not found" but it exists

**Cause:** User trying to access candidate from different company

**Solution:** Verify the candidate belongs to the user's company:
```sql
SELECT c.id, c.company_id, u.company_id as user_company_id
FROM candidates c, users u
WHERE c.id = CANDIDATE_ID AND u.id = USER_ID;
```

### Issue: Migration fails with foreign key error

**Cause:** Existing data has invalid references

**Solution:** Clean up orphaned records first:
```sql
-- Find candidates without valid company
SELECT * FROM candidates WHERE company_id NOT IN (SELECT id FROM companies);

-- Option 1: Assign to default company
UPDATE candidates SET company_id = 1 WHERE company_id IS NULL;

-- Option 2: Delete orphaned records
DELETE FROM candidates WHERE company_id NOT IN (SELECT id FROM companies);
```

---

## Best Practices

### 1. Always Set company_id When Creating Records

```python
# ✅ GOOD
candidate = Candidate(
    company_id=current_user.company_id,
    name="John Doe",
    ...
)

# ❌ BAD - Will fail with NOT NULL constraint
candidate = Candidate(
    name="John Doe",
    ...
)
```

### 2. Always Filter by company_id in Queries

```python
# ✅ GOOD
query = db.query(Candidate)
if current_user.company_id:
    query = query.filter(Candidate.company_id == current_user.company_id)

# ❌ BAD - Exposes all companies' data
query = db.query(Candidate)
```

### 3. Check Permissions Before Allowing Actions

```python
# ✅ GOOD
if current_user.role != UserRole.SUPER_ADMIN:
    raise HTTPException(403, "Only super admins can perform this action")

# ❌ BAD - No permission check
# Anyone can do anything
```

### 4. Use Dependency Injection for Authorization

```python
def require_company_admin(current_user: User):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN]:
        raise HTTPException(403, "Insufficient permissions")
    return current_user

@router.post("/")
async def create_user(
    current_user: User = Depends(require_company_admin)
):
    # Only company admins and super admins can access
    ...
```

---

## Summary

✅ **Multi-tenancy is now fully implemented**
✅ **Complete data isolation between companies**
✅ **Role-based access control (RBAC)**
✅ **Secure API endpoints with company filtering**
✅ **Migration script for existing data**

🔒 **Your clients' data is now secure and isolated!**

For questions or issues, refer to:
- `Backend/migrations/README.md` - Migration guide
- `Backend/app/models/company.py` - Company model
- `Backend/app/api/api_v1/endpoints/companies.py` - Company API
