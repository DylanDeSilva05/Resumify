#!/usr/bin/env python3
"""
Script to clear all users from the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User

def clear_all_users():
    """Delete all users from the database"""
    db = SessionLocal()

    try:
        users = db.query(User).all()
        user_count = len(users)

        if user_count == 0:
            print("✅ No users found in database")
            return True

        print(f"Found {user_count} users:")
        for user in users:
            print(f"  - {user.username} ({user.email}) - {user.user_type.value}")

        confirm = input(f"\nAre you sure you want to delete ALL {user_count} users? (yes/no): ")

        if confirm.lower() in ['yes', 'y']:
            db.query(User).delete()
            db.commit()
            print(f"✅ All {user_count} users deleted successfully")
            return True
        else:
            print("❌ Deletion cancelled")
            return False

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("⚠️  WARNING: This will delete ALL users from the database!")
    clear_all_users()