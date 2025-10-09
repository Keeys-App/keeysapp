"""
Migration script to create keys and translations tables.
Creates tables for managing translation keys and their translations.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from app.models.base import Base
from app.models.key import Key, Translation
from sqlalchemy import inspect


def create_keys_tables():
    """
    Create keys and translations tables if they don't exist.
    """
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print("Existing tables:", existing_tables)
    
    # Check if tables already exist
    if 'keys' in existing_tables and 'translations' in existing_tables:
        print("Keys and translations tables already exist. Skipping creation.")
        return
    
    print("Creating keys and translations tables...")
    
    # Create only the keys and translations tables
    Key.__table__.create(bind=engine, checkfirst=True)
    Translation.__table__.create(bind=engine, checkfirst=True)
    
    print("Keys and translations tables created successfully!")
    
    # Verify tables were created
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'keys' in existing_tables and 'translations' in existing_tables:
        print("✓ Keys table created")
        print("✓ Translations table created")
        
        # Show columns
        print("\nKeys table columns:")
        for column in inspector.get_columns('keys'):
            print(f"  - {column['name']} ({column['type']})")
        
        print("\nTranslations table columns:")
        for column in inspector.get_columns('translations'):
            print(f"  - {column['name']} ({column['type']})")
    else:
        print("ERROR: Tables were not created!")


if __name__ == "__main__":
    print("Starting keys tables migration...")
    create_keys_tables()
    print("Migration complete!")

