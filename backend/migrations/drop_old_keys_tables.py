"""
Migration script to drop old keys/translations tables.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from sqlalchemy import text


def drop_old_tables():
    """
    Drop old translations and keys tables.
    """
    print("Dropping old tables...")
    
    with engine.connect() as conn:
        # Drop tables in correct order (children first)
        conn.execute(text("DROP TABLE IF EXISTS translations CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS keys CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS translation_keys CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS locales CASCADE"))
        conn.commit()
    
    print("Old tables dropped successfully!")


if __name__ == "__main__":
    print("Starting cleanup migration...")
    drop_old_tables()
    print("Cleanup complete!")

