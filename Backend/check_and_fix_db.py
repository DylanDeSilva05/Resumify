"""
Script to check and fix database issues
"""
from app.core.database import SessionLocal
from app.models.user import User

def check_users():
    """Check all users in database"""
    db = SessionLocal()
    try:
        # Get all users
        users = db.query(User).all()

        print(f"\n=== Total Users: {len(users)} ===\n")

        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Full Name: {user.full_name}")
            print(f"User Type: {user.user_type}")
            print(f"Is Active: {user.is_active}")
            print("-" * 50)

        # Check for the specific email
        target_email = "dylandesilva05@gmail.com"
        user = db.query(User).filter(User.email == target_email).first()

        if user:
            print(f"\n⚠️ Found user with email {target_email}:")
            print(f"   ID: {user.id}, Username: {user.username}")

            # Ask if user wants to delete
            response = input(f"\nDo you want to delete this user? (yes/no): ")
            if response.lower() == 'yes':
                db.delete(user)
                db.commit()
                print(f"✅ User {user.username} deleted successfully!")
            else:
                print("❌ User not deleted.")
        else:
            print(f"\n✅ No user found with email {target_email}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
