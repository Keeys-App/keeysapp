"""
Migration: Move review_status from keys to translations

This migration:
1. Adds review_status column to translations table
2. Removes review_status column from keys table
"""

from sqlalchemy import text
from app.database import get_db
import logging

logger = logging.getLogger(__name__)


def run_migration():
    """Move review_status from keys to translations"""
    db = next(get_db())
    
    try:
        # Step 1: Add review_status column to translations table if it doesn't exist
        logger.info("Adding review_status column to translations table")
        print("Adding review_status column to translations table...")
        
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'translations' 
                AND column_name = 'review_status'
            );
        """))
        
        column_exists = result.scalar()
        
        if not column_exists:
            db.execute(text("""
                ALTER TABLE translations 
                ADD COLUMN review_status reviewstatus 
                NOT NULL DEFAULT 'NOT_REVIEWED'
            """))
            db.commit()
            print("✓ Added review_status column to translations table")
        else:
            print("✓ review_status column already exists in translations table")
        
        # Step 2: Remove review_status column from keys table if it exists
        logger.info("Removing review_status column from keys table")
        print("Removing review_status column from keys table...")
        
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'keys' 
                AND column_name = 'review_status'
            );
        """))
        
        column_exists_in_keys = result.scalar()
        
        if column_exists_in_keys:
            db.execute(text("""
                ALTER TABLE keys 
                DROP COLUMN review_status
            """))
            db.commit()
            print("✓ Removed review_status column from keys table")
        else:
            print("✓ review_status column already removed from keys table")
        
        logger.info("Successfully completed review status migration")
        print("✓ Successfully moved review_status from keys to translations")
        
    except Exception as e:
        logger.error(f"Migration failed: {type(e).__name__}: {str(e)}")
        print(f"✗ Migration failed: {type(e).__name__}: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Move review_status from keys to translations")
    print("=" * 60)
    run_migration()
    print("\nMigration completed!")

