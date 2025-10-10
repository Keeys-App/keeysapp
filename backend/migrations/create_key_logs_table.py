"""
Migration script to create key_logs table.
Creates table for auditing all changes to translation keys.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from app.models.base import Base
from app.models.key_log import KeyLog
from sqlalchemy import inspect


def create_key_logs_table():
    """
    Create key_logs table if it doesn't exist.
    """
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print("Existing tables:", existing_tables)
    
    # Check if table already exists
    if 'key_logs' in existing_tables:
        print("Key logs table already exists. Skipping creation.")
        return
    
    print("Creating key_logs table...")
    
    # Create the key_logs table
    KeyLog.__table__.create(bind=engine, checkfirst=True)
    
    print("Key logs table created successfully!")
    
    # Verify table was created
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'key_logs' in existing_tables:
        print("✓ Key logs table created")
        
        # Show columns
        print("\nKey logs table columns:")
        for column in inspector.get_columns('key_logs'):
            print(f"  - {column['name']} ({column['type']})")
    else:
        print("ERROR: Table was not created!")


if __name__ == "__main__":
    print("Starting key logs table migration...")
    create_key_logs_table()
    print("Migration complete!")

