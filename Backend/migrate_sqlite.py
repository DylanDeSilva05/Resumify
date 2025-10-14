"""
SQLite Migration Script - Add Multi-Tenancy Support
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = "resumify.db"

def backup_database():
    """Create a backup of the database"""
    backup_path = f"resumify_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

    print("=" * 60)
    print("STEP 1: CREATING BACKUP")
    print("=" * 60)

    try:
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print(f"\n✓ Backup created: {backup_path}")
        print("  (Keep this file safe!)")
        return True
    except Exception as e:
        print(f"\n✗ Backup failed: {e}")
        return False


def run_migration():
    """Run the multi-tenancy migration"""

    print("\n" + "=" * 60)
    print("STEP 2: RUNNING MIGRATION")
    print("=" * 60)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("\n1. Checking if companies table exists...")
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='companies'
        """)
        if cursor.fetchone():
            print("   ✓ Companies table already exists")
        else:
            print("   Creating companies table...")
            cursor.execute("""
                CREATE TABLE companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name VARCHAR UNIQUE NOT NULL,
                    contact_email VARCHAR NOT NULL,
                    contact_phone VARCHAR,
                    address TEXT,
                    city VARCHAR,
                    state VARCHAR,
                    country VARCHAR,
                    postal_code VARCHAR,
                    is_active BOOLEAN DEFAULT 1,
                    subscription_tier VARCHAR DEFAULT 'basic',
                    max_users INTEGER DEFAULT 5,
                    max_cv_uploads_monthly INTEGER DEFAULT 100,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME
                )
            """)
            print("   ✓ Companies table created")

        print("\n2. Creating default company...")
        cursor.execute("""
            INSERT OR IGNORE INTO companies (company_name, contact_email, is_active, subscription_tier, max_users)
            VALUES ('Default Company', 'admin@resumify.com', 1, 'enterprise', 999)
        """)

        cursor.execute("SELECT id FROM companies WHERE company_name = 'Default Company'")
        default_company_id = cursor.fetchone()[0]
        print(f"   ✓ Default company ID: {default_company_id}")

        print("\n3. Adding company_id to users table...")
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'company_id' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN company_id INTEGER")
            print("   ✓ Added company_id column")
        else:
            print("   ✓ company_id column already exists")

        print("\n4. Adding role to users table...")
        if 'role' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'company_user'")
            print("   ✓ Added role column")
        else:
            print("   ✓ role column already exists")

        print("\n5. Setting default company for existing users...")
        cursor.execute("""
            UPDATE users
            SET company_id = ?
            WHERE company_id IS NULL
        """, (default_company_id,))
        print(f"   ✓ Updated {cursor.rowcount} users")

        print("\n6. Adding company_id to candidates table...")
        cursor.execute("PRAGMA table_info(candidates)")
        candidate_columns = [col[1] for col in cursor.fetchall()]

        if 'company_id' not in candidate_columns:
            cursor.execute("ALTER TABLE candidates ADD COLUMN company_id INTEGER")
            cursor.execute(f"UPDATE candidates SET company_id = {default_company_id} WHERE company_id IS NULL")
            print(f"   ✓ Added company_id to candidates")
        else:
            print("   ✓ company_id already in candidates")

        print("\n7. Adding company_id to job_postings table...")
        cursor.execute("PRAGMA table_info(job_postings)")
        job_columns = [col[1] for col in cursor.fetchall()]

        if 'company_id' not in job_columns:
            cursor.execute("ALTER TABLE job_postings ADD COLUMN company_id INTEGER")
            cursor.execute(f"UPDATE job_postings SET company_id = {default_company_id} WHERE company_id IS NULL")
            print(f"   ✓ Added company_id to job_postings")
        else:
            print("   ✓ company_id already in job_postings")

        print("\n8. Adding company_id to cv_analyses table...")
        cursor.execute("PRAGMA table_info(cv_analyses)")
        analysis_columns = [col[1] for col in cursor.fetchall()]

        if 'company_id' not in analysis_columns:
            cursor.execute("ALTER TABLE cv_analyses ADD COLUMN company_id INTEGER")
            cursor.execute(f"UPDATE cv_analyses SET company_id = {default_company_id} WHERE company_id IS NULL")
            print(f"   ✓ Added company_id to cv_analyses")
        else:
            print("   ✓ company_id already in cv_analyses")

        print("\n9. Adding company_id to interviews table...")
        # Check if interviews table exists first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interviews'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(interviews)")
            interview_columns = [col[1] for col in cursor.fetchall()]

            if 'company_id' not in interview_columns:
                cursor.execute("ALTER TABLE interviews ADD COLUMN company_id INTEGER")
                cursor.execute(f"UPDATE interviews SET company_id = {default_company_id} WHERE company_id IS NULL")
                print(f"   ✓ Added company_id to interviews")
            else:
                print("   ✓ company_id already in interviews")
        else:
            print("   ⚠ Interviews table doesn't exist (skipped)")

        # Commit all changes
        conn.commit()

        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)

        conn.close()
        return True

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        print("\nRolling back changes...")
        conn.rollback()
        conn.close()
        return False


def verify_migration():
    """Verify the migration was successful"""

    print("\n" + "=" * 60)
    print("STEP 3: VERIFYING MIGRATION")
    print("=" * 60)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check companies
        cursor.execute("SELECT COUNT(*) FROM companies")
        company_count = cursor.fetchone()[0]
        print(f"\n✓ Companies in database: {company_count}")

        # Check users with company_id
        cursor.execute("SELECT COUNT(*) FROM users WHERE company_id IS NOT NULL")
        users_with_company = cursor.fetchone()[0]
        print(f"✓ Users with company_id: {users_with_company}")

        # Check candidates with company_id
        cursor.execute("SELECT COUNT(*) FROM candidates WHERE company_id IS NOT NULL")
        candidates_with_company = cursor.fetchone()[0]
        print(f"✓ Candidates with company_id: {candidates_with_company}")

        # List users
        print("\n" + "=" * 60)
        print("USERS AFTER MIGRATION:")
        print("=" * 60)

        cursor.execute("""
            SELECT id, username, email, company_id, role, is_active
            FROM users
        """)

        print(f"\n{'ID':<5} {'Username':<20} {'Email':<30} {'Co.ID':<8} {'Role':<15} {'Active'}")
        print("-" * 100)

        for row in cursor.fetchall():
            company_id = row[3] if row[3] is not None else 'NULL'
            role = row[4] if row[4] is not None else 'NULL'
            print(f"{row[0]:<5} {row[1]:<20} {row[2]:<30} {company_id:<8} {role:<15} {row[5]}")

        conn.close()
        return True

    except Exception as e:
        print(f"\n✗ Verification failed: {e}")
        return False


def make_user_super_admin(user_id):
    """Make a user a super admin"""

    print("\n" + "=" * 60)
    print(f"MAKING USER {user_id} A SUPER ADMIN")
    print("=" * 60)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET role = 'super_admin',
                company_id = NULL,
                is_active = 1
            WHERE id = ?
        """, (user_id,))

        conn.commit()

        if cursor.rowcount > 0:
            print(f"\n✓ User {user_id} is now a SUPER_ADMIN!")
            print(f"✓ company_id set to NULL (super admins don't belong to companies)")
            print(f"✓ Account activated")

            # Show user details
            cursor.execute("SELECT username, email FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if user:
                print(f"\nUsername: {user[0]}")
                print(f"Email: {user[1]}")
                print(f"\n🎉 You can now login with this account!")
        else:
            print(f"\n✗ User {user_id} not found")

        conn.close()
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("RESUMIFY SQLITE MIGRATION TOOL")
    print("Multi-Tenancy Implementation")
    print("=" * 60)

    if not os.path.exists(DB_PATH):
        print(f"\n✗ Database not found: {DB_PATH}")
        print("\nMake sure you're in the Backend directory!")
        return

    print("\nThis will:")
    print("  1. Create a backup of your database")
    print("  2. Add company_id and role columns to all tables")
    print("  3. Create a 'Default Company' for existing data")
    print("  4. Migrate all existing data to the default company")

    proceed = input("\nDo you want to proceed? (yes/no): ").strip().lower()

    if proceed not in ['yes', 'y']:
        print("\nMigration cancelled.")
        return

    # Step 1: Backup
    if not backup_database():
        print("\n✗ Cannot proceed without backup!")
        return

    # Step 2: Run migration
    if not run_migration():
        print("\n✗ Migration failed!")
        return

    # Step 3: Verify
    if not verify_migration():
        print("\n✗ Verification failed!")
        return

    # Step 4: Ask to make user super admin
    print("\n" + "=" * 60)
    print("FINAL STEP: SET UP SUPER ADMIN")
    print("=" * 60)

    print("\nYour users:")
    print("  1 - admin")
    print("  2 - testuser")
    print("  3 - Dylan")

    user_choice = input("\nWhich user should be super admin? (1/2/3): ").strip()

    try:
        user_id = int(user_choice)
        if user_id in [1, 2, 3]:
            make_user_super_admin(user_id)
        else:
            print("\nInvalid choice. You can run this script again to set super admin.")
    except ValueError:
        print("\nInvalid input. You can run this script again to set super admin.")

    print("\n" + "=" * 60)
    print("ALL DONE!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Restart your backend server")
    print("  2. Try logging in with your super admin account")
    print("  3. You can now create companies and manage users!")


if __name__ == "__main__":
    main()
