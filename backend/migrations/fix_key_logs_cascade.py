"""
Migration: Fix cascade delete for key_logs table

This migration ensures that key_logs are properly deleted when their parent key is deleted.
Updates the foreign key constraint to use CASCADE on delete.
"""

from sqlalchemy import text
from app.database import get_db
import logging

logger = logging.getLogger(__name__)


def run_migration():
    """Fix cascade delete for key_logs foreign key"""
    db = next(get_db())
    
    try:
        logger.info("Checking key_logs foreign key constraint...")
        
        # Check existing constraint
        result = db.execute(text("""
            SELECT 
                tc.constraint_name,
                rc.update_rule,
                rc.delete_rule
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.referential_constraints AS rc
                    ON tc.constraint_name = rc.constraint_name
            WHERE 
                tc.table_name = 'key_logs' 
                AND tc.constraint_type = 'FOREIGN KEY'
                AND rc.unique_constraint_name LIKE '%keys_pkey%';
        """))
        
        constraint_info = result.fetchone()
        
        if constraint_info:
            constraint_name, update_rule, delete_rule = constraint_info
            logger.info(f"Current constraint: {constraint_name}, delete_rule: {delete_rule}")
            print(f"Current constraint: {constraint_name}, delete_rule: {delete_rule}")
            
            if delete_rule == 'CASCADE':
                logger.info("Foreign key already has CASCADE delete rule")
                print("✓ Foreign key already has CASCADE delete rule")
                return
            
            # Drop the old constraint
            logger.info(f"Dropping old constraint: {constraint_name}")
            print(f"Dropping old constraint: {constraint_name}...")
            db.execute(text(f"ALTER TABLE key_logs DROP CONSTRAINT {constraint_name}"))
            db.commit()
            
            # Add new constraint with CASCADE
            logger.info("Adding new constraint with CASCADE delete")
            print("Adding new constraint with CASCADE delete...")
            db.execute(text("""
                ALTER TABLE key_logs 
                ADD CONSTRAINT key_logs_key_id_fkey 
                FOREIGN KEY (key_id) 
                REFERENCES keys(id) 
                ON DELETE CASCADE
            """))
            db.commit()
            
            logger.info("Successfully updated foreign key constraint")
            print("✓ Successfully updated foreign key constraint with CASCADE delete")
        else:
            logger.warning("Could not find foreign key constraint for key_logs.key_id")
            print("⚠ Could not find foreign key constraint, attempting to create it...")
            
            # Try to create the constraint with CASCADE
            db.execute(text("""
                ALTER TABLE key_logs 
                ADD CONSTRAINT key_logs_key_id_fkey 
                FOREIGN KEY (key_id) 
                REFERENCES keys(id) 
                ON DELETE CASCADE
            """))
            db.commit()
            print("✓ Created foreign key constraint with CASCADE delete")
        
    except Exception as e:
        logger.error(f"Migration failed: {type(e).__name__}: {str(e)}")
        print(f"✗ Migration failed: {type(e).__name__}: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Fix cascade delete for key_logs")
    print("=" * 60)
    run_migration()
    print("\nMigration completed!")

