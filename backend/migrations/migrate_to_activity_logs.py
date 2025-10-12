"""
Migration: Convert key_logs to universal activity_logs system

This migration:
1. Renames key_logs table to activity_logs
2. Changes key_id foreign key from CASCADE to SET NULL
3. Adds new fields: project_id, affected_user_id, metadata
4. Updates enum type from KeyActionType to ActionType
5. Adds new indexes for project_id
6. Preserves all existing data

Run this migration BEFORE deploying new code that uses ActivityLog.
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Run the migration"""
    engine = create_engine(settings.database_url)
    
    with engine.begin() as conn:
        logger.info("Starting migration to activity_logs system...")
        
        # Check if activity_logs table already exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'activity_logs'
            );
        """))
        if result.scalar():
            logger.info("✓ activity_logs table already exists, skipping migration")
            return
        
        # Check if key_logs table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'key_logs'
            );
        """))
        if not result.scalar():
            logger.warning("⚠ key_logs table does not exist, creating activity_logs from scratch")
            create_activity_logs_table(conn)
            return
        
        logger.info("Step 1: Renaming key_logs to activity_logs...")
        conn.execute(text("ALTER TABLE key_logs RENAME TO activity_logs;"))
        logger.info("✓ Table renamed")
        
        logger.info("Step 2: Adding new columns...")
        
        # Add project_id column
        conn.execute(text("""
            ALTER TABLE activity_logs 
            ADD COLUMN IF NOT EXISTS project_id INTEGER;
        """))
        
        # Add affected_user_id column
        conn.execute(text("""
            ALTER TABLE activity_logs 
            ADD COLUMN IF NOT EXISTS affected_user_id INTEGER;
        """))
        
        # Add extra_data column
        conn.execute(text("""
            ALTER TABLE activity_logs 
            ADD COLUMN IF NOT EXISTS extra_data JSONB;
        """))
        logger.info("✓ New columns added")
        
        logger.info("Step 3: Populating project_id from keys...")
        # Fill project_id for all existing logs based on their key_id
        conn.execute(text("""
            UPDATE activity_logs 
            SET project_id = keys.project_id 
            FROM keys 
            WHERE activity_logs.key_id = keys.id 
            AND activity_logs.project_id IS NULL;
        """))
        logger.info("✓ project_id populated")
        
        logger.info("Step 4: Updating foreign key constraints...")
        
        # Drop old foreign key constraint for key_id (CASCADE)
        conn.execute(text("""
            ALTER TABLE activity_logs 
            DROP CONSTRAINT IF EXISTS key_logs_key_id_fkey;
        """))
        
        # Drop old foreign key constraint for user_id
        conn.execute(text("""
            ALTER TABLE activity_logs 
            DROP CONSTRAINT IF EXISTS key_logs_user_id_fkey;
        """))
        
        # Add new foreign key constraints with SET NULL
        conn.execute(text("""
            ALTER TABLE activity_logs 
            ADD CONSTRAINT activity_logs_key_id_fkey 
            FOREIGN KEY (key_id) REFERENCES keys(id) ON DELETE SET NULL;
        """))
        
        conn.execute(text("""
            ALTER TABLE activity_logs 
            ADD CONSTRAINT activity_logs_user_id_fkey 
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
        """))
        
        conn.execute(text("""
            ALTER TABLE activity_logs 
            ADD CONSTRAINT activity_logs_project_id_fkey 
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL;
        """))
        
        conn.execute(text("""
            ALTER TABLE activity_logs 
            ADD CONSTRAINT activity_logs_affected_user_id_fkey 
            FOREIGN KEY (affected_user_id) REFERENCES users(id) ON DELETE SET NULL;
        """))
        logger.info("✓ Foreign key constraints updated")
        
        logger.info("Step 5: Updating enum type...")
        
        # Create new enum type with all action types
        conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE actiontype AS ENUM (
                    'PROJECT_CREATE',
                    'PROJECT_UPDATE_NAME',
                    'PROJECT_UPDATE_DESCRIPTION',
                    'PROJECT_UPDATE_LANGUAGES',
                    'PROJECT_UPDATE_DEFAULT_LANGUAGE',
                    'PROJECT_UPDATE_COLOR',
                    'PROJECT_UPDATE_STATUS',
                    'PROJECT_DELETE',
                    'PROJECT_EXPORT',
                    'PROJECT_IMPORT',
                    'MEMBER_ADD',
                    'MEMBER_REMOVE',
                    'MEMBER_ROLE_CHANGE',
                    'KEY_CREATE',
                    'KEY_UPDATE',
                    'KEY_UPDATE_DESCRIPTION',
                    'KEY_DELETE',
                    'TRANSLATION_UPDATE',
                    'TRANSLATION_DELETE',
                    'TRANSLATION_IMPORT',
                    'REVIEW_APPROVE',
                    'REVIEW_REJECT',
                    'REVIEW_DELETE'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        # Map old enum values to new ones
        conn.execute(text("""
            ALTER TABLE activity_logs 
            ALTER COLUMN action TYPE VARCHAR(50);
        """))
        
        # Update existing action values
        conn.execute(text("""
            UPDATE activity_logs SET action = 'KEY_CREATE' WHERE action = 'CREATE';
        """))
        conn.execute(text("""
            UPDATE activity_logs SET action = 'KEY_UPDATE' WHERE action = 'UPDATE_KEY';
        """))
        conn.execute(text("""
            UPDATE activity_logs SET action = 'KEY_UPDATE_DESCRIPTION' WHERE action = 'UPDATE_DESCRIPTION';
        """))
        conn.execute(text("""
            UPDATE activity_logs SET action = 'TRANSLATION_UPDATE' WHERE action = 'UPDATE_TRANSLATION';
        """))
        conn.execute(text("""
            UPDATE activity_logs SET action = 'TRANSLATION_DELETE' WHERE action = 'DELETE_TRANSLATION';
        """))
        conn.execute(text("""
            UPDATE activity_logs SET action = 'KEY_DELETE' WHERE action = 'DELETE';
        """))
        conn.execute(text("""
            UPDATE activity_logs SET action = 'TRANSLATION_IMPORT' WHERE action = 'IMPORT';
        """))
        
        # Convert to new enum type
        conn.execute(text("""
            ALTER TABLE activity_logs 
            ALTER COLUMN action TYPE actiontype USING action::actiontype;
        """))
        
        # Drop old enum type if exists
        conn.execute(text("""
            DROP TYPE IF EXISTS keyactiontype CASCADE;
        """))
        logger.info("✓ Enum type updated")
        
        logger.info("Step 6: Updating indexes...")
        
        # Rename old indexes
        conn.execute(text("""
            ALTER INDEX IF EXISTS ix_key_logs_key_id RENAME TO ix_activity_logs_key_id;
        """))
        conn.execute(text("""
            ALTER INDEX IF EXISTS ix_key_logs_user_id RENAME TO ix_activity_logs_user_id;
        """))
        conn.execute(text("""
            ALTER INDEX IF EXISTS ix_key_logs_action RENAME TO ix_activity_logs_action;
        """))
        conn.execute(text("""
            ALTER INDEX IF EXISTS ix_key_logs_created_at RENAME TO ix_activity_logs_created_at;
        """))
        
        # Add new indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_activity_logs_project_id 
            ON activity_logs(project_id);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_activity_logs_affected_user_id 
            ON activity_logs(affected_user_id);
        """))
        logger.info("✓ Indexes updated")
        
        logger.info("✅ Migration completed successfully!")
        
        # Print statistics
        result = conn.execute(text("SELECT COUNT(*) FROM activity_logs;"))
        count = result.scalar()
        logger.info(f"Total activity logs: {count}")


def create_activity_logs_table(conn):
    """Create activity_logs table from scratch if key_logs doesn't exist"""
    logger.info("Creating activity_logs table from scratch...")
    
    # Create enum type
    conn.execute(text("""
        DO $$ BEGIN
            CREATE TYPE actiontype AS ENUM (
                'PROJECT_CREATE',
                'PROJECT_UPDATE_NAME',
                'PROJECT_UPDATE_DESCRIPTION',
                'PROJECT_UPDATE_LANGUAGES',
                'PROJECT_UPDATE_DEFAULT_LANGUAGE',
                'PROJECT_UPDATE_COLOR',
                'PROJECT_UPDATE_STATUS',
                'PROJECT_DELETE',
                'PROJECT_EXPORT',
                'PROJECT_IMPORT',
                'MEMBER_ADD',
                'MEMBER_REMOVE',
                'MEMBER_ROLE_CHANGE',
                'KEY_CREATE',
                'KEY_UPDATE',
                'KEY_UPDATE_DESCRIPTION',
                'KEY_DELETE',
                'TRANSLATION_UPDATE',
                'TRANSLATION_DELETE',
                'TRANSLATION_IMPORT',
                'REVIEW_APPROVE',
                'REVIEW_REJECT',
                'REVIEW_DELETE'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))
    
    # Create table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id SERIAL PRIMARY KEY,
            project_id INTEGER,
            key_id INTEGER,
            user_id INTEGER,
            affected_user_id INTEGER,
            action actiontype NOT NULL,
            field_name VARCHAR(100),
            language VARCHAR(10),
            old_value TEXT,
            new_value TEXT,
            extra_data JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            CONSTRAINT activity_logs_project_id_fkey 
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
            CONSTRAINT activity_logs_key_id_fkey 
                FOREIGN KEY (key_id) REFERENCES keys(id) ON DELETE SET NULL,
            CONSTRAINT activity_logs_user_id_fkey 
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            CONSTRAINT activity_logs_affected_user_id_fkey 
                FOREIGN KEY (affected_user_id) REFERENCES users(id) ON DELETE SET NULL
        );
    """))
    
    # Create indexes
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_activity_logs_project_id ON activity_logs(project_id);
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_activity_logs_key_id ON activity_logs(key_id);
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_activity_logs_user_id ON activity_logs(user_id);
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_activity_logs_action ON activity_logs(action);
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_activity_logs_created_at ON activity_logs(created_at);
    """))
    
    logger.info("✓ activity_logs table created")


def rollback():
    """Rollback the migration (if needed)"""
    engine = create_engine(settings.database_url)
    
    with engine.begin() as conn:
        logger.info("Rolling back migration...")
        
        # This is a destructive operation, be careful!
        logger.warning("⚠ Rollback will lose project-level logs and new fields!")
        
        # Rename table back
        conn.execute(text("ALTER TABLE activity_logs RENAME TO key_logs;"))
        
        # Drop new columns
        conn.execute(text("ALTER TABLE key_logs DROP COLUMN IF EXISTS project_id;"))
        conn.execute(text("ALTER TABLE key_logs DROP COLUMN IF EXISTS affected_user_id;"))
        conn.execute(text("ALTER TABLE key_logs DROP COLUMN IF EXISTS extra_data;"))
        
        logger.info("✓ Rollback completed")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()

