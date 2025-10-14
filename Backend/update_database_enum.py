"""
Script to update the database enum type to match new role values
SQLite stores enum as text, so we need to update the actual values
"""
import sqlite3
from app.core.config import settings

def update_enum_values():
    """Update role enum values in SQLite database"""

    # Extract database path from URL
    db_path = settings.DATABASE_URL.replace('sqlite:///', '')

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check current role values
        print("\nCurrent role values in database:")
        cursor.execute("SELECT DISTINCT role FROM users")
        current_roles = cursor.fetchall()
        for role in current_roles:
            print(f"  - {role[0]}")

        # The values are already correct (company_admin, company_user, etc.)
        # The issue is SQLite is checking against some cached enum definition

        # SQLite doesn't have native enum support, so the issue might be in SQLAlchemy
        # Let's check what create_check_type did

        print("\nChecking table schema...")
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
        schema = cursor.fetchone()[0]
        print("\nCurrent users table schema:")
        print(schema)

        # Check if there's a CHECK constraint on the role column
        if 'CHECK' in schema and 'role' in schema:
            print("\n⚠️  Found CHECK constraint on role column")
            print("SQLite has a CHECK constraint that's restricting enum values.")
            print("\nTo fix this, we need to:")
            print("1. Create a new table without the CHECK constraint")
            print("2. Copy all data")
            print("3. Drop the old table")
            print("4. Rename the new table")

            response = input("\nProceed with fixing the CHECK constraint? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Cancelled.")
                return

            # Get all column definitions except the problematic CHECK constraint
            # Create new table without enum CHECK constraint
            cursor.execute("""
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    username VARCHAR NOT NULL UNIQUE,
                    email VARCHAR NOT NULL UNIQUE,
                    full_name VARCHAR NOT NULL,
                    hashed_password VARCHAR NOT NULL,
                    role VARCHAR NOT NULL DEFAULT 'company_user',
                    is_active BOOLEAN DEFAULT 1,
                    two_fa_enabled BOOLEAN DEFAULT 0,
                    two_fa_secret VARCHAR,
                    backup_codes VARCHAR,
                    failed_login_attempts INTEGER DEFAULT 0,
                    account_locked_until DATETIME,
                    last_login DATETIME,
                    password_changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    reset_otp VARCHAR,
                    reset_otp_expires_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME,
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                )
            """)

            # Copy data from old table to new table
            cursor.execute("""
                INSERT INTO users_new
                SELECT id, company_id, username, email, full_name, hashed_password,
                       role, is_active, two_fa_enabled, two_fa_secret, backup_codes,
                       failed_login_attempts, account_locked_until, last_login,
                       password_changed_at, reset_otp, reset_otp_expires_at,
                       created_at, updated_at
                FROM users
            """)

            # Drop old table
            cursor.execute("DROP TABLE users")

            # Rename new table
            cursor.execute("ALTER TABLE users_new RENAME TO users")

            conn.commit()
            print("\n✅ Successfully updated database schema!")
            print("The role column no longer has CHECK constraints.")

        else:
            print("\n✅ No CHECK constraint found. The database schema looks good.")

        # Verify final state
        print("\nFinal role distribution:")
        cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]} users")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE ENUM UPDATE SCRIPT")
    print("=" * 60)
    print("\nThis script will remove CHECK constraints on the role column")
    print("that are preventing the new role values from working.")
    print()
    update_enum_values()
