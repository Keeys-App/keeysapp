"""
Migration: Add IMPORT action type to KeyActionType enum

This migration adds the 'import' value to the keyactiontype enum in PostgreSQL.
"""

from sqlalchemy import text
from app.database import get_db
import logging

logger = logging.getLogger(__name__)


def run_migration():
    """Add IMPORT action type to keyactiontype enum"""
    db = next(get_db())
    
    try:
        # Check if 'IMPORT' value already exists (uppercase like other values)
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT 1 
                FROM pg_enum 
                WHERE enumlabel = 'IMPORT' 
                AND enumtypid = (
                    SELECT oid 
                    FROM pg_type 
                    WHERE typname = 'keyactiontype'
                )
            );
        """))
        
        exists = result.scalar()
        
        if exists:
            logger.info("'IMPORT' value already exists in keyactiontype enum")
            print("✓ 'IMPORT' value already exists in keyactiontype enum")
            return
        
        # Remove lowercase 'import' if it exists
        try:
            db.execute(text("""
                DELETE FROM pg_enum 
                WHERE enumlabel = 'import' 
                AND enumtypid = (
                    SELECT oid 
                    FROM pg_type 
                    WHERE typname = 'keyactiontype'
                )
            """))
            db.commit()
            print("Removed lowercase 'import' value")
        except Exception as e:
            print(f"Note: Could not remove lowercase 'import': {e}")
        
        # Add 'IMPORT' value to enum (uppercase like other values)
        logger.info("Adding 'IMPORT' value to keyactiontype enum")
        print("Adding 'IMPORT' value to keyactiontype enum...")
        
        db.execute(text("ALTER TYPE keyactiontype ADD VALUE 'IMPORT'"))
        db.commit()
        
        logger.info("Successfully added 'IMPORT' value to keyactiontype enum")
        print("✓ Successfully added 'IMPORT' value to keyactiontype enum")
        
    except Exception as e:
        logger.error(f"Migration failed: {type(e).__name__}: {str(e)}")
        print(f"✗ Migration failed: {type(e).__name__}: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Add IMPORT action type to KeyActionType enum")
    print("=" * 60)
    run_migration()
    print("\nMigration completed!")

