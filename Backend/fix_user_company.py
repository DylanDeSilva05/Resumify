"""
Script to check and fix user company associations and roles
"""
from app.core.database import SessionLocal
from app.models import User, Company, UserRole

def main():
    db = SessionLocal()

    try:
        # Get all users
        users = db.query(User).all()
        print("\n=== Current Users ===")
        for user in users:
            print(f"ID: {user.id}")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Role: {user.role}")
            print(f"  Company ID: {user.company_id}")
            print()

        # Get all companies
        companies = db.query(Company).all()
        print("\n=== Current Companies ===")
        for company in companies:
            print(f"ID: {company.id}")
            print(f"  Name: {company.company_name}")
            print(f"  Active: {company.is_active}")
            print()

        # Check if we need to create a company
        if not companies:
            print("No companies found. Creating default company...")
            default_company = Company(
                company_name="Default Company",
                industry="Technology",
                is_active=True,
                max_users=10,
                max_cv_uploads_monthly=1000
            )
            db.add(default_company)
            db.commit()
            db.refresh(default_company)
            print(f"Created company: {default_company.company_name} (ID: {default_company.id})")
            companies = [default_company]

        # Update users without company
        company_id = companies[0].id
        for user in users:
            if not user.company_id:
                print(f"\nUpdating user {user.username}...")
                user.company_id = company_id

                # If user is not super admin and not company admin, make them company admin
                if user.role not in [UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN]:
                    print(f"  Changing role from {user.role} to COMPANY_ADMIN")
                    user.role = UserRole.COMPANY_ADMIN

                db.commit()
                print(f"  Associated with company ID: {company_id}")
                print(f"  Role: {user.role}")

        print("\n=== Update Complete ===")
        print("Users can now access email settings!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
