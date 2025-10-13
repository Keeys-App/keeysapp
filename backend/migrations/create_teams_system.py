"""
Migration script to create teams system.
Creates teams, team_members, and project_access tables.
Updates projects table to include team_id.
Drops old project_members table as this is a new system.

Run this migration with:
    python -m migrations.create_teams_system
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from app.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upgrade():
    """
    Create teams system tables and modify projects table.
    """
    with engine.connect() as conn:
        try:
            logger.info("Starting teams system migration...")
            
            # Create teams table
            logger.info("Creating teams table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS teams (
                    id SERIAL PRIMARY KEY,
                    public_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE
                );
                CREATE INDEX IF NOT EXISTS idx_teams_public_id ON teams(public_id);
                CREATE INDEX IF NOT EXISTS idx_teams_owner_id ON teams(owner_id);
            """))
            conn.commit()
            logger.info("✓ Teams table created")
            
            # Create team_members table
            logger.info("Creating team_members table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS team_members (
                    id SERIAL PRIMARY KEY,
                    team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(team_id, user_id)
                )
            """))
            conn.commit()
            
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_team_members_team_id ON team_members(team_id)"))
            conn.commit()
            
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_team_members_user_id ON team_members(user_id)"))
            conn.commit()
            logger.info("✓ Team members table created")
            
            # Create project_access table
            logger.info("Creating project_access table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS project_access (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
                    granted_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(project_id, user_id)
                )
            """))
            conn.commit()
            
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_project_access_project_id ON project_access(project_id)"))
            conn.commit()
            
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_project_access_user_id ON project_access(user_id)"))
            conn.commit()
            logger.info("✓ Project access table created")
            
            # Check if team_id column already exists in projects
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='projects' AND column_name='team_id';
            """))
            column_exists = result.fetchone() is not None
            
            if not column_exists:
                # Add team_id column to projects table (nullable first, will be updated later)
                logger.info("Adding team_id column to projects table...")
                conn.execute(text("""
                    ALTER TABLE projects ADD COLUMN IF NOT EXISTS team_id INTEGER;
                """))
                conn.commit()
                logger.info("✓ team_id column added to projects")
            else:
                logger.info("✓ team_id column already exists in projects")
            
            # Drop old project_members table if exists
            logger.info("Checking for old project_members table...")
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='project_members';
            """))
            table_exists = result.fetchone() is not None
            
            if table_exists:
                logger.info("Dropping old project_members table...")
                conn.execute(text("DROP TABLE IF EXISTS project_members CASCADE;"))
                conn.commit()
                logger.info("✓ Old project_members table dropped")
            else:
                logger.info("✓ Old project_members table doesn't exist")
            
            logger.info("✅ Teams system migration completed successfully!")
            logger.info("")
            logger.info("NOTE: Projects table has team_id column but it's nullable.")
            logger.info("You need to:")
            logger.info("1. Create teams for existing projects")
            logger.info("2. Set team_id for all projects")
            logger.info("3. Make team_id NOT NULL and add foreign key constraint")
            
        except Exception as e:
            logger.error(f"Migration failed: {type(e).__name__}: {str(e)}")
            conn.rollback()
            raise


def downgrade():
    """
    Rollback teams system migration.
    WARNING: This will delete all teams and project access data!
    """
    with engine.connect() as conn:
        try:
            logger.info("Rolling back teams system migration...")
            
            # Remove team_id column from projects
            logger.info("Removing team_id from projects table...")
            conn.execute(text("ALTER TABLE projects DROP COLUMN IF EXISTS team_id;"))
            conn.commit()
            
            # Drop tables in reverse order
            logger.info("Dropping project_access table...")
            conn.execute(text("DROP TABLE IF EXISTS project_access CASCADE;"))
            conn.commit()
            
            logger.info("Dropping team_members table...")
            conn.execute(text("DROP TABLE IF EXISTS team_members CASCADE;"))
            conn.commit()
            
            logger.info("Dropping teams table...")
            conn.execute(text("DROP TABLE IF EXISTS teams CASCADE;"))
            conn.commit()
            
            logger.info("✅ Teams system rollback completed!")
            
        except Exception as e:
            logger.error(f"Rollback failed: {type(e).__name__}: {str(e)}")
            conn.rollback()
            raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "down":
        downgrade()
    else:
        upgrade()

