#!/usr/bin/env python3
"""
Script to drop and recreate all database tables.
WARNING: This will delete ALL data!
"""
from app.database import engine
from app.models.base import Base
from app.models.user import User  # Import to register table


def recreate_tables():
    """
    Drop all tables and recreate them with new schema.
    """
    print("⚠️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ All tables dropped")
    
    print("📝 Creating tables with new schema...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created")
    
    print("")
    print("🎉 Database schema updated successfully!")
    print("   Users table now includes:")
    print("   - id (Integer, internal)")
    print("   - public_id (UUID, public API)")
    print("   - All other fields")
    print("")
    print("You can now register new users.")


if __name__ == "__main__":
    print("")
    print("=" * 60)
    print("  ⚠️  WARNING: DROP AND RECREATE ALL TABLES")
    print("=" * 60)
    print("")
    print("This will DELETE ALL DATA in the database!")
    print("This includes:")
    print("  - All users")
    print("  - All other tables")
    print("")
    print("Use this ONLY in development!")
    print("")
    response = input("Are you ABSOLUTELY SURE? Type 'DELETE ALL DATA' to confirm: ")
    
    if response == 'DELETE ALL DATA':
        recreate_tables()
    else:
        print("Operation cancelled. No changes made.")

