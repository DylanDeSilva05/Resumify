"""
Fix role case mismatch - SQLite stores lowercase, Python expects uppercase
"""
import sqlite3

DB_PATH = "resumify.db"

def fix_roles():
    """Convert role values from lowercase to uppercase"""

    print("=" * 60)
    print("FIXING ROLE CASE MISMATCH")
    print("=" * 60)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Show current roles
        print("\nCurrent user roles:")
        cursor.execute("SELECT id, username, role FROM users")
        for row in cursor.fetchall():
            print(f"  User {row[0]} ({row[1]}): {row[2]}")

        # Fix the roles
        print("\nUpdating roles to uppercase...")

        cursor.execute("""
            UPDATE users
            SET role = 'SUPER_ADMIN'
            WHERE role = 'super_admin'
        """)
        super_admin_count = cursor.rowcount

        cursor.execute("""
            UPDATE users
            SET role = 'COMPANY_ADMIN'
            WHERE role = 'company_admin'
        """)
        company_admin_count = cursor.rowcount

        cursor.execute("""
            UPDATE users
            SET role = 'COMPANY_USER'
            WHERE role = 'company_user'
        """)
        company_user_count = cursor.rowcount

        cursor.execute("""
            UPDATE users
            SET role = 'RECRUITER'
            WHERE role = 'recruiter'
        """)
        recruiter_count = cursor.rowcount

        conn.commit()

        print(f"  ✓ Updated {super_admin_count} SUPER_ADMIN")
        print(f"  ✓ Updated {company_admin_count} COMPANY_ADMIN")
        print(f"  ✓ Updated {company_user_count} COMPANY_USER")
        print(f"  ✓ Updated {recruiter_count} RECRUITER")

        # Show updated roles
        print("\nUpdated user roles:")
        cursor.execute("SELECT id, username, role, is_active FROM users")
        for row in cursor.fetchall():
            status = "✓ Active" if row[3] else "✗ Inactive"
            print(f"  User {row[0]} ({row[1]}): {row[2] or 'NULL'} - {status}")

        conn.close()

        print("\n" + "=" * 60)
        print("✓ ROLE CASE FIX COMPLETE!")
        print("=" * 60)
        print("\nRestart your backend server and try logging in!")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


if __name__ == "__main__":
    fix_roles()
