"""
Script to create initial super admin user for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate
from app.models.user import UserRole

def create_initial_user():
    """Create an initial super admin user"""
    db = SessionLocal()

    try:
        # Check if any users exist
        from app.models.user import User
        existing_users = db.query(User).count()

        if existing_users > 0:
            print("✅ Users already exist in the database")
            users = db.query(User).all()
            for user in users:
                print(f"   - {user.username} ({user.role.value}) - {user.email}")
            return True

        # Create initial super admin (platform owner)
        user_data = UserCreate(
            username="admin",
            email="admin@resumify.com",
            full_name="Resumify Administrator",
            password="Admin@123",  # Strong password with uppercase, lowercase, number, special char
            role=UserRole.SUPER_ADMIN,
            is_active=True
        )

        print("🔄 Creating initial super admin user...")
        user = AuthService.create_user(db, user_data)

        print("✅ Initial super admin user created successfully!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role.value} (Platform Owner)")
        print(f"   Password: Admin@123")
        print("")
        print("🔐 Login credentials:")
        print("   Username: admin")
        print("   Password: Admin@123")
        print("")
        print("⚠️  IMPORTANT: Change this password after first login!")
        print("")
        print("📝 As SUPER_ADMIN, you can:")
        print("   - Create companies for your clients")
        print("   - Manage all companies and their data")
        print("   - View platform-wide analytics")

        return True

    except Exception as e:
        print(f"❌ Failed to create user: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Setting up initial user for Resumify...")
    success = create_initial_user()
    if success:
        print("🎉 Setup completed! You can now login to test the API.")
    else:
        print("💡 Please check the error above and try again.")