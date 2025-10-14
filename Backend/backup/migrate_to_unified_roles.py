"""
Database migration script to unify role systems
- Migrates data from user_type to role
- Removes user_type column
- Maps legacy roles to new unified roles
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Role mapping from old UserType to new UserRole
ROLE_MAPPING = {
    'admin_hr': 'company_admin',      # ADMIN_HR -> COMPANY_ADMIN
    'standard_hr': 'company_user',    # STANDARD_HR -> COMPANY_USER
    'recruiter_hr': 'recruiter'       # RECRUITER_HR -> RECRUITER
}


def migrate_roles():
    """Migrate user_type values to role column"""
    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        print("Starting role migration...")

        # Step 1: Check if user_type column exists
        # SQLite doesn't have information_schema, use PRAGMA instead
        if 'sqlite' in settings.DATABASE_URL:
            result = db.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]  # Column names are at index 1
            has_user_type = 'user_type' in columns
        else:
            # PostgreSQL/MySQL
            result = db.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='users' AND column_name='user_type'
            """))
            has_user_type = result.fetchone() is not None

        if not has_user_type:
            print("✓ user_type column does not exist. Migration may have already been completed.")
            return

        # Step 2: Migrate existing data from user_type to role
        print("\nStep 1: Migrating user_type values to role...")

        for old_role, new_role in ROLE_MAPPING.items():
            result = db.execute(text(f"""
                UPDATE users
                SET role = '{new_role}'
                WHERE user_type = '{old_role}'
            """))
            count = result.rowcount
            db.commit()
            print(f"  ✓ Migrated {count} users from '{old_role}' to '{new_role}'")

        # Step 3: Check for any unmapped roles
        result = db.execute(text("""
            SELECT DISTINCT user_type
            FROM users
            WHERE user_type NOT IN ('admin_hr', 'standard_hr', 'recruiter_hr')
            AND user_type IS NOT NULL
        """))
        unmapped = result.fetchall()

        if unmapped:
            print(f"\n⚠ WARNING: Found unmapped user_type values: {unmapped}")
            print("  These users will keep their current role values.")

        # Step 4: Show migration summary
        print("\nStep 2: Migration summary...")
        result = db.execute(text("""
            SELECT role, COUNT(*) as count
            FROM users
            GROUP BY role
        """))

        print("\n  Current role distribution:")
        for row in result:
            print(f"    - {row[0]}: {row[1]} users")

        # Step 5: Drop user_type column
        print("\nStep 3: Dropping user_type column...")

        # For SQLite
        if 'sqlite' in settings.DATABASE_URL:
            print("  Note: SQLite requires table recreation to drop columns.")
            print("  You'll need to recreate the table or use Alembic migrations.")
            print("  For now, the user_type column will remain but is unused.")
        else:
            # For PostgreSQL/MySQL
            db.execute(text("ALTER TABLE users DROP COLUMN user_type"))
            db.commit()
            print("  ✓ user_type column dropped successfully")

        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Restart your backend server")
        print("2. Test login with different user roles")
        print("3. Verify permissions are working correctly")

    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("UNIFIED ROLE SYSTEM MIGRATION")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Migrate user_type values to role column")
    print("2. Map legacy roles to new unified roles:")
    print("   - admin_hr      → company_admin")
    print("   - standard_hr   → company_user")
    print("   - recruiter_hr  → recruiter")
    print("3. Remove the user_type column")
    print("\n⚠  WARNING: Please backup your database before proceeding!")

    response = input("\nContinue with migration? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        migrate_roles()
    else:
        print("\nMigration cancelled.")
