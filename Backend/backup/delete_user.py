#!/usr/bin/env python3
"""
Script to delete a specific user from the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User

def delete_user_by_username(username: str):
    """Delete a user by username"""
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.username == username).first()

        if not user:
            print(f"❌ User '{username}' not found")
            return False

        print(f"Found user: {user.username} ({user.email}) - {user.user_type.value}")
        confirm = input(f"Are you sure you want to delete user '{username}'? (yes/no): ")

        if confirm.lower() in ['yes', 'y']:
            db.delete(user)
            db.commit()
            print(f"✅ User '{username}' deleted successfully")
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
    if len(sys.argv) != 2:
        print("Usage: python delete_user.py <username>")
        print("Example: python delete_user.py testuser")
        sys.exit(1)

    username = sys.argv[1]
    delete_user_by_username(username)