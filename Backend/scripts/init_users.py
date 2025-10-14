"""
Initialize database with essential user accounts
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.company import Company
from app.core.security import get_password_hash

def create_initial_users():
    """Create initial users and company in the database"""
    db = SessionLocal()

    try:
        # Check if any users exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"Database already has {existing_users} users. Skipping initialization.")
            return

        # Create or get default company
        print("Creating or getting default company...")
        company = db.query(Company).filter(Company.company_name == "Edith Cowan University").first()
        if not company:
            company = Company(
                company_name="Edith Cowan University",
                contact_email="contact@ecu.edu.au",
                contact_phone="+61 8 6304 0000",
                address="270 Joondalup Drive",
                city="Joondalup",
                state="WA",
                country="Australia",
                postal_code="6027",
                is_active=True,
                subscription_tier="premium",
                max_users=50,
                max_cv_uploads_monthly=1000,
                smtp_enabled=False
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            print(f"[OK] Created company: {company.company_name} (ID: {company.id})")
        else:
            print(f"[OK] Using existing company: {company.company_name} (ID: {company.id})")

        # Create Super Admin user (Resumify Administrator)
        print("\nCreating Super Admin user...")
        super_admin = User(
            company_id=None,  # Super admin doesn't belong to any company
            username="admin",
            email="admin@resumify.com",
            full_name="Resumify Administrator",
            hashed_password=get_password_hash("admin123"),  # Change this password!
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            two_fa_enabled=False,
            failed_login_attempts=0,
            smtp_enabled=False
        )
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        print(f"[OK] Created Super Admin: {super_admin.username}")
        print(f"  Email: {super_admin.email}")
        print(f"  Password: admin123 (CHANGE THIS!)")

        # Create Company Admin user (Dylan de Silva)
        print("\nCreating Company Admin user...")
        company_admin = User(
            company_id=company.id,
            username="Dylan",
            email="dylan@ecu.edu.au",
            full_name="Dylan de Silva",
            hashed_password=get_password_hash("dylan123"),  # Change this password!
            role=UserRole.COMPANY_ADMIN,
            is_active=True,
            two_fa_enabled=False,
            failed_login_attempts=0,
            smtp_enabled=False
        )
        db.add(company_admin)
        db.commit()
        db.refresh(company_admin)
        print(f"[OK] Created Company Admin: {company_admin.username}")
        print(f"  Email: {company_admin.email}")
        print(f"  Password: dylan123 (CHANGE THIS!)")

        # Create Company User (Dewshini Mendis)
        print("\nCreating Company User...")
        company_user = User(
            company_id=company.id,
            username="Dewshini",
            email="dewshini@ecu.edu.au",
            full_name="Dewshini Mendis",
            hashed_password=get_password_hash("dewshini123"),  # Change this password!
            role=UserRole.COMPANY_USER,
            is_active=True,
            two_fa_enabled=False,
            failed_login_attempts=0,
            smtp_enabled=False
        )
        db.add(company_user)
        db.commit()
        db.refresh(company_user)
        print(f"[OK] Created Company User: {company_user.username}")
        print(f"  Email: {company_user.email}")
        print(f"  Password: dewshini123 (CHANGE THIS!)")

        print("\n" + "="*60)
        print("[OK] Database initialization completed successfully!")
        print("="*60)
        print("\nCreated accounts:")
        print("1. Super Admin:")
        print("   Username: admin")
        print("   Password: admin123")
        print()
        print("2. Company Admin:")
        print("   Username: Dylan")
        print("   Password: dylan123")
        print()
        print("3. Company User:")
        print("   Username: Dewshini")
        print("   Password: dewshini123")
        print()
        print("WARNING: Please change these default passwords immediately!")
        print("="*60)

    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_initial_users()
