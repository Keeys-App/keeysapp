"""
Migration: Add review_status field and review action types

This migration:
1. Creates ReviewStatus enum type
2. Adds review_status column to keys table
3. Adds REVIEW_APPROVE, REVIEW_REJECT, REVIEW_DELETE to KeyActionType enum
"""

from sqlalchemy import text
from app.database import get_db
import logging

logger = logging.getLogger(__name__)


def run_migration():
    """Add review_status field and review action types"""
    db = next(get_db())
    
    try:
        # Step 1: Create ReviewStatus enum type if it doesn't exist
        logger.info("Creating ReviewStatus enum type")
        print("Creating ReviewStatus enum type...")
        
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT 1 
                FROM pg_type 
                WHERE typname = 'reviewstatus'
            );
        """))
        
        enum_exists = result.scalar()
        
        if not enum_exists:
            db.execute(text("""
                CREATE TYPE reviewstatus AS ENUM (
                    'NOT_REVIEWED',
                    'PENDING', 
                    'APPROVED',
                    'REJECTED'
                )
            """))
            db.commit()
            print("✓ Created ReviewStatus enum type")
        else:
            print("✓ ReviewStatus enum type already exists")
        
        # Step 2: Add review_status column to keys table if it doesn't exist
        logger.info("Adding review_status column to keys table")
        print("Adding review_status column to keys table...")
        
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'keys' 
                AND column_name = 'review_status'
            );
        """))
        
        column_exists = result.scalar()
        
        if not column_exists:
            db.execute(text("""
                ALTER TABLE keys 
                ADD COLUMN review_status reviewstatus 
                NOT NULL DEFAULT 'NOT_REVIEWED'
            """))
            db.commit()
            print("✓ Added review_status column to keys table")
        else:
            print("✓ review_status column already exists in keys table")
        
        # Step 3: Add REVIEW_APPROVE action type
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT 1 
                FROM pg_enum 
                WHERE enumlabel = 'REVIEW_APPROVE' 
                AND enumtypid = (
                    SELECT oid 
                    FROM pg_type 
                    WHERE typname = 'keyactiontype'
                )
            );
        """))
        
        if not result.scalar():
            logger.info("Adding 'REVIEW_APPROVE' value to keyactiontype enum")
            print("Adding 'REVIEW_APPROVE' value to keyactiontype enum...")
            db.execute(text("ALTER TYPE keyactiontype ADD VALUE 'REVIEW_APPROVE'"))
            db.commit()
            print("✓ Added 'REVIEW_APPROVE' value")
        else:
            print("✓ 'REVIEW_APPROVE' value already exists")
        
        # Step 4: Add REVIEW_REJECT action type
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT 1 
                FROM pg_enum 
                WHERE enumlabel = 'REVIEW_REJECT' 
                AND enumtypid = (
                    SELECT oid 
                    FROM pg_type 
                    WHERE typname = 'keyactiontype'
                )
            );
        """))
        
        if not result.scalar():
            logger.info("Adding 'REVIEW_REJECT' value to keyactiontype enum")
            print("Adding 'REVIEW_REJECT' value to keyactiontype enum...")
            db.execute(text("ALTER TYPE keyactiontype ADD VALUE 'REVIEW_REJECT'"))
            db.commit()
            print("✓ Added 'REVIEW_REJECT' value")
        else:
            print("✓ 'REVIEW_REJECT' value already exists")
        
        # Step 5: Add REVIEW_DELETE action type
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT 1 
                FROM pg_enum 
                WHERE enumlabel = 'REVIEW_DELETE' 
                AND enumtypid = (
                    SELECT oid 
                    FROM pg_type 
                    WHERE typname = 'keyactiontype'
                )
            );
        """))
        
        if not result.scalar():
            logger.info("Adding 'REVIEW_DELETE' value to keyactiontype enum")
            print("Adding 'REVIEW_DELETE' value to keyactiontype enum...")
            db.execute(text("ALTER TYPE keyactiontype ADD VALUE 'REVIEW_DELETE'"))
            db.commit()
            print("✓ Added 'REVIEW_DELETE' value")
        else:
            print("✓ 'REVIEW_DELETE' value already exists")
        
        logger.info("Successfully completed review status migration")
        print("✓ Successfully completed review status migration")
        
    except Exception as e:
        logger.error(f"Migration failed: {type(e).__name__}: {str(e)}")
        print(f"✗ Migration failed: {type(e).__name__}: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Add review_status and review action types")
    print("=" * 60)
    run_migration()
    print("\nMigration completed!")

