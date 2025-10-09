#!/usr/bin/env python3
"""
Script to clear all users from the database.
Use this after code changes that affect password hashing.
"""

from app.database import engine, SessionLocal
from app.models.user import User

def clear_users():
    """Clear all users 11 from the database."""
    db = SessionLocal()
    try:
        # Delete all users
        deleted = db.query(User).delete()
        db.commit()
        print(f"✅ Deleted {deleted} user(s) from the database.")
        print("You can now register new users with the updated code.")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("⚠️  This will delete all users from the database!")
    response = input("Are you sure? (yes/no): ")
    if response.lower() == 'yes':
        clear_users()
    else:
        print("Cancelled.")

