# Unified Role-Based Access Control System

## Overview

The Resumify platform now uses a **unified role system** that combines both Role-Based Access Control (RBAC) for permissions and Multi-Tenancy for data isolation in a single, coherent architecture.

## The Four Roles

### 1. SUPER_ADMIN (Platform Owner)
**Who**: Resumify system administrators (you, the platform owner)

**Scope**: Platform-wide access across all companies

**Capabilities**:
- ✅ Create and manage companies
- ✅ View and manage all companies' data
- ✅ Manage subscription tiers and limits
- ✅ Full system administration
- ✅ All permissions across all companies
- ✅ No `company_id` (not tied to any company)

**Use Cases**:
- Creating new company accounts for clients
- Managing subscription plans
- System maintenance and monitoring
- Viewing platform-wide analytics

---

### 2. COMPANY_ADMIN (Company Owner)
**Who**: Client company administrators

**Scope**: Full access within their own company only

**Capabilities**:
- ✅ Manage users within their company
- ✅ View and update company profile
- ✅ Access all HR features
- ✅ View company analytics
- ✅ Manage company settings
- ❌ Cannot modify subscription tier or limits
- ❌ Cannot access other companies' data
- ❌ Cannot create other companies

**Use Cases**:
- Managing HR team members
- Configuring company settings
- Accessing all recruitment features
- Viewing company reports

---

### 3. COMPANY_USER (Standard HR Staff)
**Who**: Regular HR team members

**Scope**: Standard HR operations within their company

**Capabilities**:
- ✅ Upload and analyze CVs
- ✅ Manage candidates
- ✅ Create and manage job postings
- ✅ Schedule interviews
- ✅ View reports
- ✅ Bulk CV analysis
- ❌ Cannot manage users
- ❌ Cannot modify company settings
- ❌ Cannot access system administration features

**Use Cases**:
- Daily recruitment operations
- CV screening and matching
- Candidate management
- Interview scheduling

---

### 4. RECRUITER (Limited Access)
**Who**: Entry-level recruiters or external recruitment partners

**Scope**: Limited recruitment operations

**Capabilities**:
- ✅ View candidates
- ✅ Upload CVs (limited)
- ✅ Schedule and manage interviews
- ✅ View basic reports
- ❌ Cannot create job postings
- ❌ Cannot delete candidates
- ❌ Cannot perform bulk operations
- ❌ No user management

**Use Cases**:
- CV screening
- Interview scheduling
- Basic candidate interaction

---

## How It Works Together

### RBAC (What can they do?)
The `role` field determines what **features and operations** a user can access:

```python
# Example: Check if user can upload CVs
if user.role in [UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN,
                  UserRole.COMPANY_USER, UserRole.RECRUITER]:
    # User can upload CVs
```

### Multi-Tenancy (What data can they see?)
The `company_id` field determines which **company's data** a user can access:

```python
# Example: Get candidates for user's company
candidates = db.query(Candidate).filter(
    Candidate.company_id == current_user.company_id
).all()

# SUPER_ADMIN bypasses this - they can see all companies
```

### Combined Example

**Scenario**: User John is a COMPANY_USER at Tesla

```python
user.role = UserRole.COMPANY_USER          # What he can do
user.company_id = 5                         # Tesla's ID

# John can:
✅ Upload CVs (has permission from COMPANY_USER role)
✅ BUT only see Tesla's CVs (filtered by company_id=5)

# John cannot:
❌ See Apple's CVs (different company_id)
❌ Manage users (COMPANY_USER role doesn't have that permission)
```

---

## Permission Matrix

| Feature | SUPER_ADMIN | COMPANY_ADMIN | COMPANY_USER | RECRUITER |
|---------|-------------|---------------|--------------|-----------|
| Create companies | ✅ | ❌ | ❌ | ❌ |
| Manage users | ✅ | ✅ (own company) | ❌ | ❌ |
| Upload CVs | ✅ | ✅ | ✅ | ✅ |
| Bulk CV upload | ✅ | ✅ | ✅ | ❌ |
| Delete candidates | ✅ | ✅ | ❌ | ❌ |
| Create job postings | ✅ | ✅ | ✅ | ❌ |
| Delete job postings | ✅ | ✅ | ❌ | ❌ |
| Schedule interviews | ✅ | ✅ | ✅ | ✅ |
| View reports | ✅ | ✅ | ✅ | ✅ |
| System analytics | ✅ | ✅ | ❌ | ❌ |
| Manage subscription | ✅ | ❌ | ❌ | ❌ |

---

## Data Isolation

### Company Data Separation
All major entities are scoped to a company:

```python
class User:
    company_id: int  # Which company this user belongs to

class Candidate:
    company_id: int  # Which company uploaded this candidate

class JobPosting:
    company_id: int  # Which company created this job

class CVAnalysis:
    company_id: int  # Which company ran this analysis
```

### Automatic Filtering
The system automatically filters data by company:

```python
# Regular users only see their company's data
if current_user.role != UserRole.SUPER_ADMIN:
    query = query.filter(Model.company_id == current_user.company_id)
```

---

## Implementation Guide

### Using Role Checks in Endpoints

```python
from app.api.deps import (
    get_super_admin_user,      # Requires SUPER_ADMIN
    get_company_admin_user,    # Requires COMPANY_ADMIN or higher
    get_company_user,          # Requires COMPANY_USER or higher
    get_recruiter_user         # Any authenticated user
)

# Example 1: Only platform owners can create companies
@router.post("/companies")
async def create_company(
    current_user: User = Depends(get_super_admin_user)
):
    # Only SUPER_ADMIN can access this
    pass

# Example 2: Company admins can manage users
@router.post("/users")
async def create_user(
    current_user: User = Depends(get_company_admin_user)
):
    # SUPER_ADMIN and COMPANY_ADMIN can access this
    pass
```

### Using Permission-Based Checks

```python
from app.core.permissions import Permission
from app.api.deps import require_permission

# Example: Check specific permission
@router.post("/candidates")
async def create_candidate(
    current_user: User = Depends(require_permission(Permission.UPLOAD_CV))
):
    # Only users with UPLOAD_CV permission can access
    pass
```

---

## Migration from Old System

### Old System (Deprecated)
```python
# Old enum - REMOVED
class UserType(str, enum.Enum):
    ADMIN_HR = "admin_hr"
    STANDARD_HR = "standard_hr"
    RECRUITER_HR = "recruiter_hr"

# Old field - REMOVED
user.user_type
```

### New System
```python
# New unified enum
class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    COMPANY_ADMIN = "company_admin"
    COMPANY_USER = "company_user"
    RECRUITER = "recruiter"

# New field
user.role
```

### Role Mapping
| Old UserType | New UserRole |
|--------------|--------------|
| ADMIN_HR | COMPANY_ADMIN |
| STANDARD_HR | COMPANY_USER |
| RECRUITER_HR | RECRUITER |

---

## Database Migration

Run the migration script to convert existing data:

```bash
cd Backend
python migrate_to_unified_roles.py
```

This script will:
1. Migrate `user_type` values to `role` column
2. Map old roles to new roles automatically
3. Remove the `user_type` column
4. Show migration summary

---

## API Changes

### Login Response
```json
{
  "access_token": "...",
  "user_id": 123,
  "username": "john@tesla.com",
  "role": "company_user",  // Changed from user_type
  "two_fa_required": false
}
```

### User Response
```json
{
  "id": 123,
  "username": "john",
  "email": "john@tesla.com",
  "full_name": "John Doe",
  "role": "company_user",  // Changed from user_type
  "company_id": 5,
  "is_active": true
}
```

---

## Testing

### Test User Creation
```bash
# Create SUPER_ADMIN (only via script or database)
python setup_initial_user.py

# Create COMPANY_ADMIN
POST /api/v1/users
{
  "username": "admin@company.com",
  "role": "company_admin",
  "company_id": 1,
  ...
}

# Create COMPANY_USER
POST /api/v1/users
{
  "username": "user@company.com",
  "role": "company_user",
  "company_id": 1,
  ...
}
```

### Test Permissions
```bash
# As COMPANY_USER - should succeed
POST /api/v1/candidates
Authorization: Bearer <company_user_token>

# As RECRUITER - should fail (no permission to delete)
DELETE /api/v1/candidates/123
Authorization: Bearer <recruiter_token>

# As SUPER_ADMIN - should succeed (all permissions)
POST /api/v1/companies
Authorization: Bearer <super_admin_token>
```

---

## Benefits of Unified System

1. **Simpler**: One role field instead of two (role + user_type)
2. **Clearer**: Role name describes both permissions and scope
3. **Scalable**: Easy to add new roles or permissions
4. **Consistent**: Same role system used everywhere
5. **Secure**: Clear separation between platform and company access

---

## Summary

| Aspect | Old System | New System |
|--------|------------|------------|
| Role field | `user_type` (UserType enum) | `role` (UserRole enum) |
| # of roles | 3 | 4 |
| Multi-tenant | Separate system | Integrated |
| Platform admin | No dedicated role | SUPER_ADMIN |
| Consistency | Two overlapping systems | One unified system |
