"""
Script to recreate the database with the new unified role system
This will delete the old database and create a fresh one
"""
import os
from app.core.config import settings
from app.core.database import Base, engine
from app.models import *  # Import all models

def recreate_database():
    """Delete old database and create fresh one with new schema"""

    # Extract database path from URL
    db_path = settings.DATABASE_URL.replace('sqlite:///', '')

    print("=" * 60)
    print("DATABASE RECREATION SCRIPT")
    print("=" * 60)
    print(f"\nDatabase file: {db_path}")

    # Check if database exists
    if os.path.exists(db_path):
        print("\n⚠️  WARNING: This will DELETE all existing data!")
        print("   Make sure you have a backup if needed.")

        response = input("\nDelete existing database and recreate? (yes/no): ")

        if response.lower() not in ['yes', 'y']:
            print("\nCancelled.")
            return

        # Delete the database file
        os.remove(db_path)
        print(f"\n✓ Deleted old database: {db_path}")
    else:
        print("\n✓ No existing database found.")

    # Create all tables with new schema
    print("\nCreating new database with unified role system...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database created successfully!")

    print("\n" + "=" * 60)
    print("DATABASE RECREATION COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Create a super admin user:")
    print("   python setup_initial_user.py")
    print("\n2. Start your backend server:")
    print("   python main.py")
    print("\n3. The new role system is now active!")
    print("   - super_admin")
    print("   - company_admin")
    print("   - company_user")
    print("   - recruiter")


if __name__ == "__main__":
    recreate_database()
