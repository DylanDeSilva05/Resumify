"""
Script to diagnose and fix login issues after multi-tenancy changes
Run this BEFORE running the migration if you need to login
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Update this with your actual database URL
DATABASE_URL = "postgresql://username:password@localhost:5432/resumify_db"

def check_database_status():
    """Check if migration has been run"""
    print("=" * 60)
    print("CHECKING DATABASE STATUS")
    print("=" * 60)

    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()

        # Check if companies table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'companies'
            );
        """))
        companies_exists = result.scalar()

        # Check if users.company_id exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'company_id'
            );
        """))
        company_id_exists = result.scalar()

        # Check if users.role exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'role'
            );
        """))
        role_exists = result.scalar()

        print(f"\n✓ Database connection: SUCCESS")
        print(f"{'✓' if companies_exists else '✗'} Companies table exists: {companies_exists}")
        print(f"{'✓' if company_id_exists else '✗'} users.company_id column exists: {company_id_exists}")
        print(f"{'✓' if role_exists else '✗'} users.role column exists: {role_exists}")

        if not companies_exists or not company_id_exists or not role_exists:
            print("\n⚠️  MIGRATION HAS NOT BEEN RUN YET!")
            print("   Your login credentials should still work.")
            print("   The issue is likely with the code changes, not the database.")
            return False
        else:
            print("\n✓ MIGRATION HAS BEEN RUN")
            return True

    except Exception as e:
        print(f"\n✗ Database connection failed: {e}")
        print("\nPossible issues:")
        print("1. Database is not running")
        print("2. Wrong DATABASE_URL in this script")
        print("3. Database 'resumify_db' doesn't exist")
        return None
    finally:
        if 'conn' in locals():
            conn.close()


def list_users():
    """List all users in the database"""
    print("\n" + "=" * 60)
    print("LISTING ALL USERS")
    print("=" * 60)

    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()

        # Check if migration has been run
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'role'
            );
        """))
        migration_run = result.scalar()

        if migration_run:
            # Migration has been run - show new columns
            result = conn.execute(text("""
                SELECT id, username, email, full_name, company_id, role, is_active
                FROM users
                ORDER BY id;
            """))

            print(f"\n{'ID':<5} {'Username':<20} {'Email':<30} {'Company ID':<12} {'Role':<15} {'Active'}")
            print("-" * 110)

            for row in result:
                print(f"{row[0]:<5} {row[1]:<20} {row[2]:<30} {str(row[4] or 'NULL'):<12} {row[5] or 'NULL':<15} {row[6]}")
        else:
            # Migration not run - show old columns
            result = conn.execute(text("""
                SELECT id, username, email, full_name, user_type, is_active
                FROM users
                ORDER BY id;
            """))

            print(f"\n{'ID':<5} {'Username':<20} {'Email':<30} {'User Type':<15} {'Active'}")
            print("-" * 90)

            for row in result:
                print(f"{row[0]:<5} {row[1]:<20} {row[2]:<30} {row[4] or 'NULL':<15} {row[5]}")

        conn.close()

    except Exception as e:
        print(f"\n✗ Error listing users: {e}")


def test_login(username: str):
    """Test if a user exists and is active"""
    print("\n" + "=" * 60)
    print(f"TESTING LOGIN FOR: {username}")
    print("=" * 60)

    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()

        result = conn.execute(
            text("SELECT id, username, email, is_active FROM users WHERE username = :username"),
            {"username": username}
        )

        user = result.fetchone()

        if not user:
            print(f"\n✗ User '{username}' NOT FOUND in database")
            print("\nPossible solutions:")
            print("1. Check if username is spelled correctly")
            print("2. User may have been deleted")
            print("3. Create a new user account")
        else:
            print(f"\n✓ User found:")
            print(f"  ID: {user[0]}")
            print(f"  Username: {user[1]}")
            print(f"  Email: {user[2]}")
            print(f"  Active: {user[3]}")

            if not user[3]:
                print(f"\n✗ Account is INACTIVE!")
                print(f"\nTo activate, run:")
                print(f"  UPDATE users SET is_active = TRUE WHERE id = {user[0]};")
            else:
                print(f"\n✓ Account is active - login should work!")

        conn.close()

    except Exception as e:
        print(f"\n✗ Error testing login: {e}")


def fix_user_for_migration(user_id: int):
    """Make a user a super admin with no company (for testing)"""
    print("\n" + "=" * 60)
    print(f"MAKING USER {user_id} A SUPER ADMIN")
    print("=" * 60)

    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()

        # Check if migration has been run
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'role'
            );
        """))
        migration_run = result.scalar()

        if not migration_run:
            print("\n⚠️  Migration hasn't been run yet.")
            print("   Cannot set role - role column doesn't exist.")
            print("   Run the migration first.")
            return

        # Update user to super admin
        conn.execute(
            text("""
                UPDATE users
                SET role = 'super_admin'::userrole,
                    company_id = NULL,
                    is_active = TRUE
                WHERE id = :user_id
            """),
            {"user_id": user_id}
        )
        conn.commit()

        print(f"\n✓ User {user_id} is now a SUPER_ADMIN with no company_id")
        print(f"✓ Account is active")
        print(f"\nYou should now be able to login!")

        conn.close()

    except Exception as e:
        print(f"\n✗ Error updating user: {e}")


def main():
    print("\n" + "=" * 60)
    print("RESUMIFY LOGIN DIAGNOSTIC TOOL")
    print("=" * 60)

    # First check database status
    migration_run = check_database_status()

    # List all users
    list_users()

    # Interactive menu
    print("\n" + "=" * 60)
    print("OPTIONS:")
    print("=" * 60)
    print("1. Test a specific username")
    print("2. Make a user super admin (after migration)")
    print("3. Exit")

    choice = input("\nEnter your choice (1-3): ").strip()

    if choice == "1":
        username = input("Enter username to test: ").strip()
        test_login(username)
    elif choice == "2":
        if migration_run:
            user_id = input("Enter user ID to make super admin: ").strip()
            try:
                user_id = int(user_id)
                fix_user_for_migration(user_id)
            except ValueError:
                print("Invalid user ID")
        else:
            print("\n⚠️  Cannot set super admin - migration not run yet")
    elif choice == "3":
        print("\nExiting...")
    else:
        print("\nInvalid choice")


if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: Update DATABASE_URL at the top of this script!")
    print(f"   Current: {DATABASE_URL}\n")

    proceed = input("Have you updated the DATABASE_URL? (yes/no): ").strip().lower()
    if proceed in ['yes', 'y']:
        main()
    else:
        print("\nPlease update DATABASE_URL in the script first, then run again.")
