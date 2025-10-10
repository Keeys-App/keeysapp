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

