#!/usr/bin/env python3
"""
Script to list all users in the database.
"""

from app.database import SessionLocal
from app.models.user import User

def list_users():
    """List all users in the database."""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("❌ No users found in the database.")
            print("💡 You need to register a new user first!")
            print("   Go to http://localhost:5173 and click 'Sign up'")
        else:
            print(f"✅ Found {len(users)} user(s):\n")
            for user in users:
                print(f"ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Username: {user.username}")
                print(f"Active: {user.is_active}")
                print(f"Superuser: {user.is_superuser}")
                print(f"Created: {user.created_at}")
                print("-" * 40)
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()

