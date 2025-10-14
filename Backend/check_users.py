#!/usr/bin/env python3
"""
Script to check users in the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User

def check_users():
    """Check all users in the database"""
    db = SessionLocal()

    try:
        users = db.query(User).all()

        print(f"Found {len(users)} users in database:")
        print("-" * 80)

        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Full Name: {user.full_name}")
            print(f"User Type: {user.user_type}")
            print(f"Active: {user.is_active}")
            print(f"2FA Enabled: {user.two_fa_enabled}")
            print(f"Created: {user.created_at}")
            print("-" * 40)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()