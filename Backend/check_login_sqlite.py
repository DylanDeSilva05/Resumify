"""
SQLite version - Check and fix login issues
"""
import sqlite3
import os

# SQLite database path
DB_PATH = "resumify.db"

def check_database():
    """Check if database exists and what tables/columns it has"""
    print("=" * 60)
    print("CHECKING SQLITE DATABASE")
    print("=" * 60)

    if not os.path.exists(DB_PATH):
        print(f"\n✗ Database file NOT FOUND: {DB_PATH}")
        print("  Make sure you're in the Backend directory")
        return False

    print(f"\n✓ Database file found: {DB_PATH}")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if users table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='users';
        """)
        users_table = cursor.fetchone()

        if not users_table:
            print("✗ Users table NOT FOUND!")
            return False

        print("✓ Users table exists")

        # Get all columns in users table
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()

        print("\nColumns in users table:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

        # Check for new columns
        column_names = [col[1] for col in columns]

        has_company_id = 'company_id' in column_names
        has_role = 'role' in column_names
        has_companies_table = False

        # Check if companies table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='companies';
        """)
        companies_table = cursor.fetchone()
        has_companies_table = companies_table is not None

        print("\nMigration status:")
        print(f"  {'✓' if has_companies_table else '✗'} companies table exists: {has_companies_table}")
        print(f"  {'✓' if has_company_id else '✗'} users.company_id column exists: {has_company_id}")
        print(f"  {'✓' if has_role else '✗'} users.role column exists: {has_role}")

        if has_companies_table and has_company_id and has_role:
            print("\n✓ MIGRATION HAS BEEN RUN")
            migration_run = True
        else:
            print("\n✗ MIGRATION HAS NOT BEEN RUN")
            migration_run = False

        conn.close()
        return migration_run

    except Exception as e:
        print(f"\n✗ Error checking database: {e}")
        return False


def list_users(migration_run):
    """List all users"""
    print("\n" + "=" * 60)
    print("ALL USERS IN DATABASE")
    print("=" * 60)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if migration_run:
            # Show new columns
            cursor.execute("""
                SELECT id, username, email, full_name, company_id, role, is_active
                FROM users
                ORDER BY id;
            """)

            print(f"\n{'ID':<5} {'Username':<20} {'Email':<30} {'Co.ID':<8} {'Role':<15} {'Active'}")
            print("-" * 100)

            for row in cursor.fetchall():
                company_id = row[4] if row[4] is not None else 'NULL'
                role = row[5] if row[5] is not None else 'NULL'
                print(f"{row[0]:<5} {row[1]:<20} {row[2]:<30} {company_id:<8} {role:<15} {row[6]}")
        else:
            # Show old columns
            cursor.execute("""
                SELECT id, username, email, full_name, user_type, is_active
                FROM users
                ORDER BY id;
            """)

            print(f"\n{'ID':<5} {'Username':<20} {'Email':<30} {'Type':<15} {'Active'}")
            print("-" * 85)

            for row in cursor.fetchall():
                user_type = row[4] if row[4] is not None else 'NULL'
                print(f"{row[0]:<5} {row[1]:<20} {row[2]:<30} {user_type:<15} {row[5]}")

        conn.close()

    except Exception as e:
        print(f"\n✗ Error listing users: {e}")


def test_user(username):
    """Test if a specific user can login"""
    print("\n" + "=" * 60)
    print(f"TESTING USER: {username}")
    print("=" * 60)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, username, email, is_active
            FROM users
            WHERE username = ?
        """, (username,))

        user = cursor.fetchone()

        if not user:
            print(f"\n✗ User '{username}' NOT FOUND")
            print("\nPossible issues:")
            print("  1. Username spelled wrong")
            print("  2. User doesn't exist")
            print("  3. Create a new user")
        else:
            print(f"\n✓ User found!")
            print(f"  ID: {user[0]}")
            print(f"  Username: {user[1]}")
            print(f"  Email: {user[2]}")
            print(f"  Active: {user[3]}")

            if not user[3]:
                print(f"\n✗ Account is INACTIVE!")
                print(f"\nTo fix, run:")
                print(f"  python fix_account.py {user[0]}")
            else:
                print(f"\n✓ Account is active")
                print(f"✓ Login should work!")

        conn.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")


def activate_user(user_id):
    """Activate a user account"""
    print(f"\nActivating user ID {user_id}...")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET is_active = 1
            WHERE id = ?
        """, (user_id,))

        conn.commit()

        if cursor.rowcount > 0:
            print(f"✓ User {user_id} activated!")
        else:
            print(f"✗ User {user_id} not found")

        conn.close()

    except Exception as e:
        print(f"✗ Error: {e}")


def fix_user_after_migration(user_id):
    """Fix user account after migration - make super admin"""
    print(f"\nMaking user ID {user_id} a super admin...")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if role column exists
        cursor.execute("PRAGMA table_info(users);")
        columns = [col[1] for col in cursor.fetchall()]

        if 'role' not in columns:
            print("✗ Migration not run yet - 'role' column doesn't exist")
            print("  Run the migration first!")
            conn.close()
            return

        cursor.execute("""
            UPDATE users
            SET role = 'super_admin',
                company_id = NULL,
                is_active = 1
            WHERE id = ?
        """, (user_id,))

        conn.commit()

        if cursor.rowcount > 0:
            print(f"✓ User {user_id} is now a SUPER_ADMIN!")
            print(f"✓ company_id set to NULL")
            print(f"✓ Account activated")
        else:
            print(f"✗ User {user_id} not found")

        conn.close()

    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    print("\n" + "=" * 60)
    print("RESUMIFY LOGIN DIAGNOSTIC TOOL (SQLite)")
    print("=" * 60)

    # Check database
    migration_run = check_database()

    if migration_run is False:
        print("\nDatabase found but migration not run yet.")

    # List users
    list_users(migration_run)

    # Menu
    print("\n" + "=" * 60)
    print("OPTIONS:")
    print("=" * 60)
    print("1. Test a specific username")
    print("2. Activate a user account")
    print("3. Make user super admin (after migration)")
    print("4. Exit")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        username = input("Enter username: ").strip()
        test_user(username)
    elif choice == "2":
        user_id = input("Enter user ID: ").strip()
        try:
            activate_user(int(user_id))
        except ValueError:
            print("Invalid user ID")
    elif choice == "3":
        if migration_run:
            user_id = input("Enter user ID: ").strip()
            try:
                fix_user_after_migration(int(user_id))
            except ValueError:
                print("Invalid user ID")
        else:
            print("\n✗ Migration not run yet!")
    else:
        print("\nExiting...")


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"\n✗ Database not found: {DB_PATH}")
        print("\nMake sure you're running this from the Backend directory:")
        print("  cd Backend")
        print("  python check_login_sqlite.py")
    else:
        main()
