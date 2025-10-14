# Login Troubleshooting Guide

## Why You Can't Login After Multi-Tenancy Changes

There are **two possible reasons**:

### Reason 1: Migration NOT Run Yet (Most Likely)
- Database still has old schema
- Code has been updated but database hasn't
- **Your old credentials SHOULD still work**
- Problem is likely in the updated code files

### Reason 2: Migration Already Run
- Database has new `company_id` and `role` columns
- Your user account needs to be updated for new schema
- **Need to set role and company_id**

---

## Step 1: Check Which Situation You're In

### Option A: Using the Diagnostic Script

1. **Update the database URL** in `Backend/check_and_fix_login.py`:
   ```python
   DATABASE_URL = "postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/resumify_db"
   ```

2. **Run the script**:
   ```bash
   cd Backend
   python check_and_fix_login.py
   ```

3. **Follow the prompts** to:
   - See if migration was run
   - List all users in database
   - Test your username
   - Fix user account if needed

### Option B: Manual Database Check

Connect to your database and run:

```sql
-- Check if migration was run
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'users';

-- If you see 'company_id' and 'role' columns, migration was run
-- If you only see 'user_type', migration was NOT run
```

---

## Solution for Each Situation

### If Migration NOT Run Yet

**The issue is that the code expects new columns that don't exist yet.**

**Quick Fix - Temporarily Revert Code Changes:**

1. **Revert User model temporarily**:
   ```bash
   cd Backend/app/models
   git checkout user.py  # If using git
   ```

   Or manually change `user.py` line 33-34:
   ```python
   # Comment out this line temporarily:
   # company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
   ```

2. **Restart your backend server**

3. **Try logging in again**

4. **After successful login, run the migration** (see below)

**Permanent Fix - Run the Migration:**

See "Running the Migration" section below.

---

### If Migration WAS Run Already

**Your user account needs `role` set and possibly `company_id`.**

**Fix 1: Using the Diagnostic Script**

```bash
python check_and_fix_login.py
# Choose option 2: Make user super admin
# Enter your user ID (usually 1)
```

**Fix 2: Using SQL Directly**

```sql
-- Make yourself a super admin (replace 1 with your user ID)
UPDATE users
SET role = 'super_admin'::userrole,
    company_id = NULL,  -- Super admins don't need company_id
    is_active = TRUE
WHERE id = 1;

-- Or if you know your username:
UPDATE users
SET role = 'super_admin'::userrole,
    company_id = NULL,
    is_active = TRUE
WHERE username = 'YOUR_USERNAME';
```

**Fix 3: Assign to Default Company**

```sql
-- If you want to be assigned to a company instead:
UPDATE users
SET role = 'company_admin'::userrole,
    company_id = (SELECT id FROM companies WHERE company_name = 'Default Company'),
    is_active = TRUE
WHERE id = 1;
```

---

## Running the Migration (If Not Done Yet)

### Prerequisites

1. **Backup your database first!**
   ```bash
   # PostgreSQL
   pg_dump -U postgres -d resumify_db > backup.sql

   # Or use pgAdmin to create backup
   ```

2. **Make sure database is running**

3. **Update database connection** in `.env` file if needed

### Run Migration

**Option 1: Using psql**

```bash
psql -U postgres -d resumify_db -f Backend/migrations/add_multi_tenancy.sql
```

**Option 2: Using pgAdmin**
1. Open pgAdmin
2. Connect to your database
3. Open Query Tool
4. Load `Backend/migrations/add_multi_tenancy.sql`
5. Execute

**Option 3: Using DBeaver or another GUI**
1. Connect to database
2. Open SQL Editor
3. Paste contents of `Backend/migrations/add_multi_tenancy.sql`
4. Execute

### After Migration

1. **Make yourself super admin** (see SQL above)
2. **Restart backend server**
3. **Try logging in**

---

## Common Login Error Messages

### Error: "User must be associated with a company"

**Cause:** User has `company_id = NULL` but is not a super admin

**Fix:**
```sql
-- Option 1: Make super admin
UPDATE users SET role = 'super_admin'::userrole WHERE id = YOUR_ID;

-- Option 2: Assign to company
UPDATE users
SET company_id = (SELECT id FROM companies LIMIT 1)
WHERE id = YOUR_ID;
```

### Error: "column users.company_id does not exist"

**Cause:** Migration not run yet, but code expects new columns

**Fix:** Run the migration (see above)

### Error: "Incorrect username or password"

**Causes:**
1. Wrong credentials
2. Account is inactive
3. Account is locked (too many failed attempts)

**Fix:**
```sql
-- Check user status
SELECT id, username, is_active, failed_login_attempts
FROM users
WHERE username = 'YOUR_USERNAME';

-- Activate account if needed
UPDATE users SET is_active = TRUE WHERE username = 'YOUR_USERNAME';

-- Reset failed login attempts
UPDATE users SET failed_login_attempts = 0 WHERE username = 'YOUR_USERNAME';
```

### Error: "type userrole does not exist"

**Cause:** Migration was partially run or failed

**Fix:** Re-run the migration script completely

---

## Emergency: Reset Everything

If nothing works, you can create a fresh super admin user:

```sql
-- Create a new super admin user
INSERT INTO users (
    username,
    email,
    full_name,
    hashed_password,
    role,
    company_id,
    is_active
) VALUES (
    'superadmin',
    'admin@resumify.com',
    'Super Admin',
    '$2b$12$KIXxQX6E8LzQiGq2VH0F1uBGN9M.vNR3l.gXyJ5HQAZ9nEYJvLv5i',  -- password: "admin123"
    'super_admin'::userrole,
    NULL,
    TRUE
);
```

**Login with:**
- Username: `superadmin`
- Password: `admin123`

⚠️ **CHANGE THIS PASSWORD IMMEDIATELY AFTER LOGIN!**

---

## Quick Checklist

- [ ] Database is running
- [ ] You know your username
- [ ] You ran the diagnostic script OR checked database manually
- [ ] You know if migration was run or not
- [ ] If migration run: Set your role to super_admin
- [ ] If migration NOT run: Either revert code changes OR run migration
- [ ] Backend server restarted after changes
- [ ] Account is active (`is_active = TRUE`)
- [ ] No account lockout (`failed_login_attempts < 5`)

---

## Still Can't Login?

### Check Backend Logs

Start your backend with logging:

```bash
cd Backend
python -m uvicorn app.main:app --reload --log-level debug
```

Try to login and watch for errors in the console.

### Check Frontend Console

Open browser dev tools (F12) → Console tab → Try login → See error messages

### Common Issues

1. **Frontend can't reach backend**
   - Check backend is running on correct port
   - Check CORS settings in `Backend/app/core/config.py`

2. **Database connection failed**
   - Check `DATABASE_URL` in `.env` file
   - Check database service is running
   - Check credentials are correct

3. **Password hash mismatch**
   - Old password hashes should still work
   - If not, reset password via SQL (see Emergency section)

---

## Need More Help?

1. Run diagnostic script and share output
2. Check backend logs for specific error
3. Verify database schema matches expected state
4. Test with a fresh super admin account

---

## What We Changed (Technical Details)

### Old Schema (Before Multi-Tenancy)
```python
class User:
    id
    username
    email
    hashed_password
    user_type  # Enum: admin_hr, standard_hr, recruiter_hr
    is_active
```

### New Schema (After Multi-Tenancy)
```python
class User:
    id
    username
    email
    hashed_password
    company_id  # Foreign key to companies table (nullable for super_admin)
    role  # Enum: super_admin, company_admin, company_user, recruiter
    user_type  # Legacy field - kept for backward compatibility
    is_active
```

**The Problem:** Code now expects `role` and `company_id`, but:
- If migration not run: Database doesn't have these columns yet
- If migration run: Your user doesn't have `role` set (defaults to NULL or company_user)

**The Solution:** Either run migration + update user, OR temporarily revert code changes
