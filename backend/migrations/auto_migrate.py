#!/usr/bin/env python3
"""
Auto-migration script that runs on application startup.
Safe to run multiple times - checks if migration is needed first.
"""
import uuid
import logging
from sqlalchemy import text, inspect
from app.database import engine, SessionLocal
from app.models.user import User

logger = logging.getLogger(__name__)


def check_column_exists(table_name: str, column_name: str) -> bool:
    """
    Check if a column exists in a table.
    
    Args:
        table_name: Name of the table
        column_name: Name of the column
        
    Returns:
        True if column exists, False otherwise
    """
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def migrate_add_public_id_if_needed():
    """
    Add public_id column if it doesn't exist.
    Safe to run multiple times.
    """
    try:
        # Check if column already exists
        if check_column_exists('users', 'public_id'):
            logger.info("✅ Migration: public_id column already exists, skipping")
            return True
        
        logger.info("🔄 Migration: Adding public_id column to users table")
        
        with engine.connect() as connection:
            # Add the column (nullable first)
            connection.execute(text("""
                ALTER TABLE users 
                ADD COLUMN public_id UUID
            """))
            connection.commit()
            logger.info("✅ Column added")
            
            # Generate UUIDs for existing users
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
                    logger.info(f"✅ Generated UUIDs for {count} user(s)")
            finally:
                db.close()
            
            # Make column NOT NULL and add index
            connection.execute(text("""
                ALTER TABLE users 
                ALTER COLUMN public_id SET NOT NULL
            """))
            
            connection.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_users_public_id ON users(public_id)
            """))
            connection.commit()
            
            logger.info("✅ Migration: public_id column added successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {type(e).__name__}: {str(e)}")
        # Don't crash the app, just log the error
        # In production, you might want to fail the deployment instead
        return False


def migrate_add_default_language_if_needed():
    """
    Add default_language column to projects table if it doesn't exist.
    Safe to run multiple times.
    """
    try:
        # Check if column already exists
        if check_column_exists('projects', 'default_language'):
            logger.info("✅ Migration: default_language column already exists, skipping")
            return True
        
        logger.info("🔄 Migration: Adding default_language column to projects table")
        
        with engine.connect() as connection:
            connection.execute(text("""
                ALTER TABLE projects
                ADD COLUMN IF NOT EXISTS default_language VARCHAR(10)
            """))
            connection.commit()
            logger.info("✅ Migration: default_language column added successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {type(e).__name__}: {str(e)}")
        return False


def migrate_add_tags_support_if_needed():
    """
    Add tags column to keys table and available_tags column to projects table if they don't exist.
    Safe to run multiple times.
    """
    try:
        keys_has_tags = check_column_exists('keys', 'tags')
        projects_has_tags = check_column_exists('projects', 'available_tags')
        
        if keys_has_tags and projects_has_tags:
            logger.info("✅ Migration: tags support already exists, skipping")
            return True
        
        logger.info("🔄 Migration: Adding tags support to keys and projects")
        
        with engine.connect() as connection:
            # Add tags column to keys table
            if not keys_has_tags:
                logger.info("Adding tags column to keys table...")
                connection.execute(text("""
                    ALTER TABLE keys 
                    ADD COLUMN IF NOT EXISTS tags JSON DEFAULT '[]'::json NOT NULL
                """))
            
            # Add available_tags column to projects table
            if not projects_has_tags:
                logger.info("Adding available_tags column to projects table...")
                connection.execute(text("""
                    ALTER TABLE projects 
                    ADD COLUMN IF NOT EXISTS available_tags JSON DEFAULT '[]'::json NOT NULL
                """))
            
            connection.commit()
            logger.info("✅ Migration: tags support added successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {type(e).__name__}: {str(e)}")
        return False


def migrate_create_key_logs_table_if_needed():
    """
    Create key_logs table if it doesn't exist.
    Safe to run multiple times.
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'key_logs' in existing_tables:
            logger.info("✅ Migration: key_logs table already exists, skipping")
            return True
        
        logger.info("🔄 Migration: Creating key_logs table")
        
        # Import here to avoid circular imports
        from app.models.key_log import KeyLog
        
        # Create the table
        KeyLog.__table__.create(bind=engine, checkfirst=True)
        
        logger.info("✅ Migration: key_logs table created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {type(e).__name__}: {str(e)}")
        return False


def migrate_add_import_action_type_if_needed():
    """
    Add IMPORT action type to keyactiontype enum if it doesn't exist.
    Safe to run multiple times.
    """
    try:
        with engine.connect() as connection:
            # Check if 'IMPORT' value already exists
            result = connection.execute(text("""
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
                logger.info("✅ Migration: IMPORT action type already exists, skipping")
                return True
            
            logger.info("🔄 Migration: Adding IMPORT action type to keyactiontype enum")
            
            # Remove lowercase 'import' if it exists
            try:
                connection.execute(text("""
                    DELETE FROM pg_enum 
                    WHERE enumlabel = 'import' 
                    AND enumtypid = (
                        SELECT oid 
                        FROM pg_type 
                        WHERE typname = 'keyactiontype'
                    )
                """))
                connection.commit()
            except Exception:
                pass  # Ignore if doesn't exist
            
            # Add 'IMPORT' value to enum
            connection.execute(text("ALTER TYPE keyactiontype ADD VALUE 'IMPORT'"))
            connection.commit()
            
            logger.info("✅ Migration: IMPORT action type added successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {type(e).__name__}: {str(e)}")
        return False


def migrate_fix_key_logs_cascade_if_needed():
    """
    Fix cascade delete for key_logs foreign key if needed.
    Safe to run multiple times.
    """
    try:
        with engine.connect() as connection:
            # Check existing constraint
            result = connection.execute(text("""
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
                
                if delete_rule == 'CASCADE':
                    logger.info("✅ Migration: key_logs CASCADE delete already exists, skipping")
                    return True
                
                # Drop the old constraint and add new one with CASCADE
                logger.info(f"Updating constraint {constraint_name} with CASCADE delete")
                connection.execute(text(f"ALTER TABLE key_logs DROP CONSTRAINT {constraint_name}"))
                connection.execute(text("""
                    ALTER TABLE key_logs 
                    ADD CONSTRAINT key_logs_key_id_fkey 
                    FOREIGN KEY (key_id) 
                    REFERENCES keys(id) 
                    ON DELETE CASCADE
                """))
                connection.commit()
                logger.info("✅ Migration: key_logs CASCADE delete constraint updated")
            else:
                # Try to create the constraint with CASCADE
                logger.info("Creating key_logs foreign key constraint with CASCADE")
                connection.execute(text("""
                    ALTER TABLE key_logs 
                    ADD CONSTRAINT key_logs_key_id_fkey 
                    FOREIGN KEY (key_id) 
                    REFERENCES keys(id) 
                    ON DELETE CASCADE
                """))
                connection.commit()
                logger.info("✅ Migration: key_logs CASCADE delete constraint created")
            
            return True
            
    except Exception as e:
        logger.error(f"Migration fix_key_logs_cascade failed: {type(e).__name__}: {str(e)}")
        return False


def migrate_add_review_status_if_needed():
    """
    Add review_status field and review action types if needed.
    Safe to run multiple times.
    """
    try:
        with engine.connect() as connection:
            # Check if ReviewStatus enum exists
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM pg_type 
                    WHERE typname = 'reviewstatus'
                );
            """))
            
            enum_exists = result.scalar()
            
            if not enum_exists:
                logger.info("Creating ReviewStatus enum type")
                connection.execute(text("""
                    CREATE TYPE reviewstatus AS ENUM (
                        'NOT_REVIEWED',
                        'PENDING', 
                        'APPROVED',
                        'REJECTED'
                    )
                """))
                connection.commit()
                logger.info("✅ Created ReviewStatus enum type")
            else:
                logger.info("✅ ReviewStatus enum type already exists")
            
            # Check if review_status column exists
            if check_column_exists('keys', 'review_status'):
                logger.info("✅ Migration: review_status column already exists")
            else:
                logger.info("Adding review_status column to keys table")
                connection.execute(text("""
                    ALTER TABLE keys 
                    ADD COLUMN review_status reviewstatus 
                    NOT NULL DEFAULT 'NOT_REVIEWED'
                """))
                connection.commit()
                logger.info("✅ Added review_status column to keys table")
            
            # Add REVIEW_APPROVE action type
            result = connection.execute(text("""
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
                connection.execute(text("ALTER TYPE keyactiontype ADD VALUE 'REVIEW_APPROVE'"))
                connection.commit()
                logger.info("✅ Added 'REVIEW_APPROVE' value")
            
            # Add REVIEW_REJECT action type
            result = connection.execute(text("""
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
                connection.execute(text("ALTER TYPE keyactiontype ADD VALUE 'REVIEW_REJECT'"))
                connection.commit()
                logger.info("✅ Added 'REVIEW_REJECT' value")
            
            # Add REVIEW_DELETE action type
            result = connection.execute(text("""
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
                connection.execute(text("ALTER TYPE keyactiontype ADD VALUE 'REVIEW_DELETE'"))
                connection.commit()
                logger.info("✅ Added 'REVIEW_DELETE' value")
            
            logger.info("✅ Migration: review_status completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {type(e).__name__}: {str(e)}")
        return False


def run_all_migrations():
    """
    Run all pending migrations.
    This is called automatically on application startup.
    """
    logger.info("🔄 Checking for pending migrations...")
    
    migrations = [
        ("add_public_id", migrate_add_public_id_if_needed),
        ("add_default_language", migrate_add_default_language_if_needed),
        ("add_tags_support", migrate_add_tags_support_if_needed),
        ("create_key_logs_table", migrate_create_key_logs_table_if_needed),
        ("add_import_action_type", migrate_add_import_action_type_if_needed),
        ("fix_key_logs_cascade", migrate_fix_key_logs_cascade_if_needed),
        ("add_review_status", migrate_add_review_status_if_needed),
        # Add more migrations here as needed
    ]
    
    success_count = 0
    for name, migration_func in migrations:
        logger.info(f"Checking migration: {name}")
        if migration_func():
            success_count += 1
    
    logger.info(f"✅ Migrations check complete: {success_count}/{len(migrations)} successful")
    return success_count == len(migrations)


if __name__ == "__main__":
    # For manual testing
    logging.basicConfig(level=logging.INFO)
    print("Running migrations...")
    if run_all_migrations():
        print("✅ All migrations completed successfully")
    else:
        print("❌ Some migrations failed")

