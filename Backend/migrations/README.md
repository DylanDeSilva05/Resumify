# Database Migrations

This directory contains database migration scripts for Resumify.

## Multi-Tenancy Migration

**File:** `add_multi_tenancy.sql`

**Purpose:** Adds multi-tenant support to enable data isolation between different companies using Resumify.

### What This Migration Does:

1. **Creates `companies` table** - Stores company/organization information
2. **Adds `company_id`** to all data tables (users, candidates, job_postings, cv_analyses, interviews)
3. **Creates default company** - Migrates existing data to a "Default Company"
4. **Adds new role system** - Introduces SUPER_ADMIN, COMPANY_ADMIN, COMPANY_USER, RECRUITER roles
5. **Sets up foreign keys** - Ensures referential integrity and cascading deletes

### Before Running:

⚠️ **IMPORTANT: BACKUP YOUR DATABASE FIRST!**

```bash
# PostgreSQL backup example
pg_dump -U your_username -d resumify > backup_before_migration.sql

# Or use your database management tool
```

### How to Run:

#### Option 1: Using psql (PostgreSQL)
```bash
psql -U your_username -d resumify -f migrations/add_multi_tenancy.sql
```

#### Option 2: Using Python script
```python
# From Backend directory
python -c "
from app.core.database import engine
from sqlalchemy import text

with open('migrations/add_multi_tenancy.sql', 'r') as f:
    migration_sql = f.read()

with engine.begin() as conn:
    # Execute each statement
    for statement in migration_sql.split(';'):
        if statement.strip():
            conn.execute(text(statement))

print('Migration completed!')
"
```

#### Option 3: Using a database GUI tool
- Open pgAdmin, DBeaver, or your preferred tool
- Connect to your database
- Open and execute `add_multi_tenancy.sql`

### After Running:

1. **Verify the migration:**
   ```sql
   -- Check companies table
   SELECT * FROM companies;

   -- Check that all users have company_id
   SELECT id, username, company_id, role FROM users;

   -- Check that all candidates have company_id
   SELECT COUNT(*) FROM candidates WHERE company_id IS NULL;
   -- Should return 0
   ```

2. **Update your first admin user:**
   ```sql
   -- Make yourself a SUPER_ADMIN
   UPDATE users
   SET role = 'super_admin'::userrole,
       company_id = NULL
   WHERE email = 'your_admin@email.com';
   ```

### Rollback (if needed):

If something goes wrong, restore from backup:

```bash
# PostgreSQL restore example
psql -U your_username -d resumify < backup_before_migration.sql
```

### Next Steps After Migration:

1. Restart your backend application
2. The new Company model will be available
3. API endpoints will need to be updated to filter by company_id (see code updates)
4. Test with multiple companies to ensure data isolation

### Changes to Application Code:

After running this migration, the following code changes are required:

1. **All API queries must filter by company_id**
2. **New company management endpoints** need to be created
3. **Authentication must include company context**
4. **Super admins can create new companies**
5. **Company admins can create users within their company**

See the updated API endpoint files for implementation details.
