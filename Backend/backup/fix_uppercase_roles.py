"""
Quick fix script to migrate uppercase user_type values
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Role mapping including uppercase variants
ROLE_MAPPING = {
    'ADMIN_HR': 'company_admin',
    'STANDARD_HR': 'company_user',
    'RECRUITER_HR': 'recruiter',
    'admin_hr': 'company_admin',
    'standard_hr': 'company_user',
    'recruiter_hr': 'recruiter'
}

def fix_roles():
    """Fix uppercase user_type values"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        print("Fixing uppercase role values...")

        # Migrate uppercase values
        for old_role, new_role in ROLE_MAPPING.items():
            result = db.execute(text(f"""
                UPDATE users
                SET role = '{new_role}'
                WHERE user_type = '{old_role}' OR role = '{old_role}'
            """))
            count = result.rowcount
            db.commit()
            if count > 0:
                print(f"  ✓ Fixed {count} users from '{old_role}' to '{new_role}'")

        # Show final distribution
        print("\nFinal role distribution:")
        result = db.execute(text("""
            SELECT role, COUNT(*) as count
            FROM users
            GROUP BY role
        """))

        for row in result:
            print(f"  - {row[0]}: {row[1]} users")

        print("\n✅ All roles fixed successfully!")

    except Exception as e:
        print(f"\n❌ Fix failed: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    fix_roles()
