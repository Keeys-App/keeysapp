#!/usr/bin/env python3
"""
Migration script to add public_id (UUID) column to existing users table.
Run this once to upgrade existing database schema.
"""
import uuid
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models.user import User


def migrate_add_public_id():
    """
    Add public_id column to users table and generate UUIDs for existing users.
    """
    print("🔄 Starting migration: Add public_id to users table")
    
    with engine.connect() as connection:
        try:
            # Check if column already exists
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='public_id'
            """))
            
            if result.fetchone():
                print("✅ Column public_id already exists. No migration needed.")
                return
            
            print("📝 Adding public_id column...")
            
            # Add the column (nullable first)
            connection.execute(text("""
                ALTER TABLE users 
                ADD COLUMN public_id UUID
            """))
            connection.commit()
            print("✅ Column added")
            
            # Generate UUIDs for existing users
            print("📝 Generating UUIDs for existing users...")
            db = SessionLocal()
            try:
                users = db.query(User).all()
                count = 0
                for user in users:
                    if not user.public_id:
                        user.public_id = uuid.uuid4()
                        count += 1
                
                if count > 0:
                    db.commit()
                    print(f"✅ Generated UUIDs for {count} user(s)")
                else:
                    print("ℹ️  No users found or all users already have UUIDs")
            finally:
                db.close()
            
            # Make column NOT NULL and add index
            print("📝 Adding constraints...")
            connection.execute(text("""
                ALTER TABLE users 
                ALTER COLUMN public_id SET NOT NULL
            """))
            
            connection.execute(text("""
                CREATE UNIQUE INDEX idx_users_public_id ON users(public_id)
            """))
            connection.commit()
            
            print("✅ Migration completed successfully!")
            print("")
            print("🎉 Users table now has public_id column")
            print("   - UUIDs generated for all existing users")
            print("   - Column is NOT NULL and UNIQUE")
            print("   - Index created for performance")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            print("")
            print("💡 Alternative: Drop and recreate the table")
            print("   WARNING: This will delete all users!")
            print("")
            print("   Option 1: Manual SQL")
            print("   DROP TABLE users;")
            print("   Then restart the application to recreate table")
            print("")
            print("   Option 2: Python script")
            print("   python clear_users.py")
            print("   Then restart application")
            raise


if __name__ == "__main__":
    print("")
    print("=" * 60)
    print("  MIGRATION: Add public_id (UUID) to users table")
    print("=" * 60)
    print("")
    print("This will modify the users table structure.")
    print("Make sure you have a backup of your database!")
    print("")
    response = input("Continue? (yes/no): ")
    
    if response.lower() == 'yes':
        migrate_add_public_id()
    else:
        print("Migration cancelled.")

