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


def migrate_move_review_to_translations_if_needed():
    """
    Move review_status from keys to translations if needed.
    Safe to run multiple times.
    """
    try:
        with engine.connect() as connection:
            # Check if review_status column exists in translations
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'translations' 
                    AND column_name = 'review_status'
                );
            """))
            
            translations_has_column = result.scalar()
            
            if not translations_has_column:
                logger.info("Adding review_status column to translations table")
                connection.execute(text("""
                    ALTER TABLE translations 
                    ADD COLUMN review_status reviewstatus 
                    NOT NULL DEFAULT 'NOT_REVIEWED'
                """))
                connection.commit()
                logger.info("✅ Added review_status column to translations table")
            else:
                logger.info("✅ review_status column already exists in translations table")
            
            # Check if review_status column exists in keys
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'keys' 
                    AND column_name = 'review_status'
                );
            """))
            
            keys_has_column = result.scalar()
            
            if keys_has_column:
                logger.info("Removing review_status column from keys table")
                connection.execute(text("""
                    ALTER TABLE keys 
                    DROP COLUMN review_status
                """))
                connection.commit()
                logger.info("✅ Removed review_status column from keys table")
            else:
                logger.info("✅ review_status column already removed from keys table")
            
            return True
            
    except Exception as e:
        logger.error(f"Migration move_review_to_translations failed: {type(e).__name__}: {str(e)}")
        return False


def migrate_to_activity_logs_if_needed():
    """
    Migrate from key_logs to universal activity_logs system.
    Safe to run multiple times.
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'activity_logs' in existing_tables:
            logger.info("✅ Migration: activity_logs table already exists, skipping")
            return True
        
        if 'key_logs' not in existing_tables:
            logger.info("✅ Migration: No key_logs table to migrate, will create activity_logs")
            # Create activity_logs table from scratch
            from app.models.activity_log import ActivityLog
            ActivityLog.__table__.create(bind=engine, checkfirst=True)
            logger.info("✅ Migration: activity_logs table created successfully")
            return True
        
        logger.info("🔄 Migration: Converting key_logs to activity_logs")
         
        # Run the migration script
        from migrations.migrate_to_activity_logs import migrate
        migrate()
        
        logger.info("✅ Migration: activity_logs conversion completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {type(e).__name__}: {str(e)}")
        return False


def migrate_add_ai_translation_action_type_if_needed():
    """
    Add TRANSLATION_AI_UPDATE action type to enum.
    Safe to run multiple times.
    """
    try:
        logger.info("🔄 Migration: Adding TRANSLATION_AI_UPDATE action type")
        
        with engine.connect() as connection:
            # Check if enum value exists by querying pg_enum
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM pg_type t 
                    JOIN pg_enum e ON t.oid = e.enumtypid 
                    WHERE t.typname = 'actiontype' 
                    AND e.enumlabel = 'TRANSLATION_AI_UPDATE'
                )
            """))
            exists = result.scalar()
            
            if exists:
                logger.info("✅ Migration: TRANSLATION_AI_UPDATE already exists, skipping")
                return True
            
            # Add the new enum value
            logger.info("Adding TRANSLATION_AI_UPDATE to actiontype enum...")
            connection.execute(
                text("ALTER TYPE actiontype ADD VALUE 'TRANSLATION_AI_UPDATE'")
            )
            connection.commit()
            logger.info("✅ Migration: TRANSLATION_AI_UPDATE added successfully")
            return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        return False


def migrate_add_team_action_types_if_needed():
    """
    Add team-related action types to enum (TEAM_CREATE, TEAM_UPDATE_NAME, etc.).
    Safe to run multiple times.
    """
    try:
        logger.info("🔄 Migration: Adding team action types")
        
        new_types = [
            'TEAM_CREATE',
            'TEAM_UPDATE_NAME',
            'TEAM_UPDATE_DESCRIPTION',
            'TEAM_DELETE',
            'TEAM_INVITE'
        ]
        
        with engine.connect() as connection:
            for action_type in new_types:
                # Check if enum value exists
                result = connection.execute(text(f"""
                    SELECT EXISTS (
                        SELECT 1 
                        FROM pg_type t 
                        JOIN pg_enum e ON t.oid = e.enumtypid 
                        WHERE t.typname = 'actiontype' 
                        AND e.enumlabel = '{action_type}'
                    )
                """))
                exists = result.scalar()
                
                if not exists:
                    logger.info(f"Adding {action_type} to actiontype enum...")
                    connection.execute(
                        text(f"ALTER TYPE actiontype ADD VALUE '{action_type}'")
                    )
                    connection.commit()
                    logger.info(f"✅ {action_type} added successfully")
                else:
                    logger.info(f"✅ {action_type} already exists, skipping")
            
            logger.info("✅ Migration: Team action types completed successfully")
            return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        return False


def migrate_add_team_id_to_activity_logs_if_needed():
    """
    Add team_id column to activity_logs table for team-level logging.
    Safe to run multiple times.
    """
    try:
        # Check if column already exists
        if check_column_exists('activity_logs', 'team_id'):
            logger.info("✅ Migration: team_id column already exists in activity_logs, skipping")
            return True
        
        logger.info("🔄 Migration: Adding team_id column to activity_logs table")
        
        with engine.connect() as connection:
            # Add the column (nullable)
            connection.execute(text("""
                ALTER TABLE activity_logs 
                ADD COLUMN team_id INTEGER REFERENCES teams(id) ON DELETE SET NULL
            """))
            
            # Add index
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_activity_logs_team_id ON activity_logs(team_id)
            """))
            
            connection.commit()
            logger.info("✅ Migration: team_id column added successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {type(e).__name__}: {str(e)}")
        return False


def migrate_set_default_project_status_if_needed():
    """
    Ensure all projects have a status set (default to 'active' for NULL/empty values).
    Safe to run multiple times.
    """
    try:
        logger.info("🔄 Migration: Checking project status values...")
        
        with engine.connect() as connection:
            # Update NULL or empty status values to 'active'
            result = connection.execute(text("""
                UPDATE projects 
                SET status = 'active' 
                WHERE status IS NULL OR status = ''
            """))
            
            updated_count = result.rowcount
            connection.commit()
            
            if updated_count > 0:
                logger.info(f"✅ Migration: Updated {updated_count} projects with default status 'active'")
            else:
                logger.info("✅ Migration: All projects already have status set")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {type(e).__name__}: {str(e)}")
        return False


def migrate_create_teams_system_if_needed():
    """
    Create teams system tables and add team_id to projects.
    Creates default teams for existing projects.
    Safe to run multiple times.
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        with engine.connect() as connection:
            # Check if teams table exists
            if 'teams' not in existing_tables:
                logger.info("🔄 Migration: Creating teams table...")
                connection.execute(text("""
                    CREATE TABLE teams (
                        id SERIAL PRIMARY KEY,
                        public_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE
                    );
                    CREATE INDEX idx_teams_public_id ON teams(public_id);
                    CREATE INDEX idx_teams_owner_id ON teams(owner_id);
                """))
                connection.commit()
                logger.info("✅ Teams table created")
            else:
                logger.info("✅ Teams table already exists")
            
            # Check if team_members table exists
            if 'team_members' not in existing_tables:
                logger.info("🔄 Migration: Creating team_members table...")
                connection.execute(text("""
                    CREATE TABLE team_members (
                        id SERIAL PRIMARY KEY,
                        team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        role VARCHAR(20) NOT NULL DEFAULT 'viewer',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(team_id, user_id)
                    );
                    CREATE INDEX idx_team_members_team_id ON team_members(team_id);
                    CREATE INDEX idx_team_members_user_id ON team_members(user_id);
                """))
                connection.commit()
                logger.info("✅ Team members table created")
            else:
                logger.info("✅ Team members table already exists")
            
            # Check if project_access table exists
            if 'project_access' not in existing_tables:
                logger.info("🔄 Migration: Creating project_access table...")
                connection.execute(text("""
                    CREATE TABLE project_access (
                        id SERIAL PRIMARY KEY,
                        project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        role VARCHAR(20) NOT NULL DEFAULT 'viewer',
                        granted_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(project_id, user_id)
                    );
                    CREATE INDEX idx_project_access_project_id ON project_access(project_id);
                    CREATE INDEX idx_project_access_user_id ON project_access(user_id);
                """))
                connection.commit()
                logger.info("✅ Project access table created")
            else:
                logger.info("✅ Project access table already exists")
            
            # Check if team_id column exists in projects
            team_id_exists = check_column_exists('projects', 'team_id')
            
            if not team_id_exists:
                logger.info("🔄 Migration: Adding team_id column to projects table...")
                connection.execute(text("""
                    ALTER TABLE projects ADD COLUMN team_id INTEGER;
                """))
                connection.commit()
                logger.info("✅ team_id column added to projects")
            else:
                logger.info("✅ team_id column already exists in projects")
            
            # Create teams for existing projects without team_id
            logger.info("🔄 Migration: Creating teams for projects without team_id...")
            result = connection.execute(text("""
                SELECT id, owner_id, name 
                FROM projects 
                WHERE team_id IS NULL
            """))
            projects_without_team = result.fetchall()
            
            if projects_without_team:
                logger.info(f"Found {len(projects_without_team)} projects without team_id")
                
                # Group projects by owner
                owners = {}
                for project_id, owner_id, project_name in projects_without_team:
                    if owner_id not in owners:
                        owners[owner_id] = []
                    owners[owner_id].append((project_id, project_name))
                
                # Create team for each owner and assign projects
                for owner_id, projects in owners.items():
                    # Get user info
                    user_result = connection.execute(text("""
                        SELECT username, email FROM users WHERE id = :owner_id
                    """), {"owner_id": owner_id})
                    user = user_result.fetchone()
                    
                    if not user:
                        logger.warning(f"Owner {owner_id} not found, skipping projects")
                        continue
                    
                    username = user[0] or user[1].split('@')[0]
                    team_name = f"{username}'s Team"
                    
                    # Check if team already exists for this owner
                    team_result = connection.execute(text("""
                        SELECT id FROM teams WHERE owner_id = :owner_id LIMIT 1
                    """), {"owner_id": owner_id})
                    team = team_result.fetchone()
                    
                    if team:
                        team_id = team[0]
                        logger.info(f"Using existing team {team_id} for owner {owner_id}")
                    else:
                        # Create new team
                        team_result = connection.execute(text("""
                            INSERT INTO teams (name, description, owner_id)
                            VALUES (:name, :description, :owner_id)
                            RETURNING id
                        """), {
                            "name": team_name,
                            "description": f"Default team for {username}",
                            "owner_id": owner_id
                        })
                        team_id = team_result.fetchone()[0]
                        connection.commit()
                        logger.info(f"Created team {team_id} for owner {owner_id}")
                    
                    # Assign all projects to this team
                    for project_id, project_name in projects:
                        connection.execute(text("""
                            UPDATE projects SET team_id = :team_id WHERE id = :project_id
                        """), {"team_id": team_id, "project_id": project_id})
                        logger.info(f"Assigned project {project_id} ({project_name}) to team {team_id}")
                    
                    connection.commit()
                
                logger.info(f"✅ Created teams and assigned {len(projects_without_team)} projects")
            else:
                logger.info("✅ All projects already have team_id")
            
            # Add NOT NULL constraint and foreign key if not present
            logger.info("🔄 Migration: Checking team_id constraints...")
            
            # Check if foreign key exists
            fk_result = connection.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'projects' 
                AND constraint_type = 'FOREIGN KEY'
                AND constraint_name LIKE '%team_id%'
            """))
            fk_exists = fk_result.fetchone() is not None
            
            if not fk_exists:
                # First, make sure all projects have team_id (shouldn't happen, but safety check)
                null_check = connection.execute(text("""
                    SELECT COUNT(*) FROM projects WHERE team_id IS NULL
                """))
                null_count = null_check.fetchone()[0]
                
                if null_count > 0:
                    logger.warning(f"Found {null_count} projects with NULL team_id, cannot add constraints")
                else:
                    logger.info("🔄 Migration: Adding NOT NULL constraint and foreign key to team_id...")
                    
                    # Add NOT NULL constraint
                    connection.execute(text("""
                        ALTER TABLE projects ALTER COLUMN team_id SET NOT NULL;
                    """))
                    
                    # Add foreign key constraint
                    connection.execute(text("""
                        ALTER TABLE projects 
                        ADD CONSTRAINT projects_team_id_fkey 
                        FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE;
                    """))
                    
                    connection.commit()
                    logger.info("✅ Added NOT NULL constraint and foreign key to team_id")
            else:
                logger.info("✅ team_id constraints already exist")
            
            logger.info("✅ Migration: Teams system completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {type(e).__name__}: {str(e)}")
        return False


def migrate_add_onboarding_completed_if_needed():
    """
    Add onboarding_completed column to users table if it doesn't exist.
    Safe to run multiple times.
    """
    try:
        # Check if column already exists
        if check_column_exists('users', 'onboarding_completed'):
            logger.info("✅ Migration: onboarding_completed column already exists, skipping")
            return True
        
        logger.info("🔄 Migration: Adding onboarding_completed column to users table")
        
        with engine.connect() as connection:
            # Add onboarding_completed column with default False
            connection.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE
            """))
            connection.commit()
            
            logger.info("✅ Migration: onboarding_completed column added successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {type(e).__name__}: {str(e)}")
        return False


def migrate_add_keys_batch_import_action_type_if_needed():
    """
    Add KEYS_BATCH_IMPORT action type to actiontype enum.
    Safe to run multiple times.
    """
    try:
        logger.info("🔄 Migration: Adding KEYS_BATCH_IMPORT action type")
        
        with engine.connect() as connection:
            # Check if enum value exists by querying pg_enum
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM pg_type t 
                    JOIN pg_enum e ON t.oid = e.enumtypid 
                    WHERE t.typname = 'actiontype' 
                    AND e.enumlabel = 'KEYS_BATCH_IMPORT'
                )
            """))
            exists = result.scalar()
            
            if exists:
                logger.info("✅ Migration: KEYS_BATCH_IMPORT already exists, skipping")
                return True
            
            # Add the new enum value
            logger.info("Adding KEYS_BATCH_IMPORT to actiontype enum...")
            connection.execute(
                text("ALTER TYPE actiontype ADD VALUE 'KEYS_BATCH_IMPORT'")
            )
            connection.commit()
            logger.info("✅ Migration: KEYS_BATCH_IMPORT added successfully")
            return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        return False


def migrate_create_password_reset_tokens_if_needed():
    """
    Create password_reset_tokens table if it doesn't exist.
    Safe to run multiple times.
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'password_reset_tokens' in existing_tables:
            logger.info("✅ Migration: password_reset_tokens table already exists, skipping")
            return True
        
        logger.info("🔄 Migration: Creating password_reset_tokens table")
        
        with engine.connect() as connection:
            connection.execute(text("""
                CREATE TABLE password_reset_tokens (
                    id SERIAL PRIMARY KEY,
                    token VARCHAR(255) NOT NULL UNIQUE,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    used BOOLEAN DEFAULT FALSE NOT NULL
                )
            """))
            
            # Create index on token for fast lookups
            connection.execute(text("""
                CREATE INDEX ix_password_reset_tokens_token ON password_reset_tokens(token)
            """))
            
            # Create index on user_id for cleanup queries
            connection.execute(text("""
                CREATE INDEX ix_password_reset_tokens_user_id ON password_reset_tokens(user_id)
            """))
            
            connection.commit()
        
        logger.info("✅ Migration: password_reset_tokens table created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {type(e).__name__}: {str(e)}")
        return False


def migrate_add_is_plural_to_keys_if_needed():
    """
    Add is_plural column to keys table if it doesn't exist.
    Safe to run multiple times.
    """
    try:
        # Check if column already exists
        if check_column_exists('keys', 'is_plural'):
            logger.info("✅ Migration: is_plural column already exists, skipping")
            return True
        
        logger.info("🔄 Migration: Adding is_plural column to keys table")
        
        with engine.connect() as connection:
            connection.execute(text("""
                ALTER TABLE keys 
                ADD COLUMN IF NOT EXISTS is_plural BOOLEAN NOT NULL DEFAULT FALSE
            """))
            connection.commit()
            
            logger.info("✅ Migration: is_plural column added successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {type(e).__name__}: {str(e)}")
        return False


def migrate_create_github_connections_if_needed():
    """
    Create github_connections table if it doesn't exist.
    GitHub connections are linked to Teams (not Users).
    Safe to run multiple times.
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'github_connections' in existing_tables:
            logger.info("✅ Migration: github_connections table already exists, skipping")
            return True
        
        logger.info("🔄 Migration: Creating github_connections table")
        
        with engine.connect() as connection:
            connection.execute(text("""
                CREATE TABLE github_connections (
                    id SERIAL PRIMARY KEY,
                    public_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
                    team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
                    connected_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    access_token TEXT NOT NULL,
                    token_type VARCHAR(50) DEFAULT 'bearer',
                    scope VARCHAR(500),
                    github_user_id VARCHAR(50) NOT NULL,
                    github_username VARCHAR(255) NOT NULL,
                    github_avatar_url VARCHAR(500),
                    github_email VARCHAR(255),
                    connected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE
                );
                
                CREATE UNIQUE INDEX idx_github_connections_public_id ON github_connections(public_id);
                CREATE INDEX idx_github_connections_team_id ON github_connections(team_id);
                CREATE INDEX idx_github_connections_connected_by ON github_connections(connected_by_user_id);
                CREATE INDEX idx_github_connections_github_user_id ON github_connections(github_user_id);
                
                -- Unique constraint: one team can have only one connection per GitHub account
                CREATE UNIQUE INDEX idx_github_connections_team_github ON github_connections(team_id, github_user_id);
            """))
            connection.commit()
            
            logger.info("✅ Migration: github_connections table created successfully")
            return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {type(e).__name__}: {str(e)}")
        return False


def migrate_create_repositories_if_needed():
    """
    Create repositories table if it doesn't exist.
    Repositories link GitHub repos to projects for localization.
    Safe to run multiple times.
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'repositories' in existing_tables:
            logger.info("✅ Migration: repositories table already exists, skipping")
            return True
        
        logger.info("🔄 Migration: Creating repositories table")
        
        with engine.connect() as connection:
            connection.execute(text("""
                CREATE TABLE repositories (
                    id SERIAL PRIMARY KEY,
                    public_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
                    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    github_connection_id INTEGER REFERENCES github_connections(id) ON DELETE SET NULL,
                    github_repo_id VARCHAR(50) NOT NULL,
                    repo_owner VARCHAR(255) NOT NULL,
                    repo_name VARCHAR(255) NOT NULL,
                    default_branch VARCHAR(255) DEFAULT 'main',
                    i18n_framework VARCHAR(50),
                    source_patterns JSON DEFAULT '[]',
                    locale_path VARCHAR(500),
                    connected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE
                );
                
                CREATE UNIQUE INDEX idx_repositories_public_id ON repositories(public_id);
                CREATE INDEX idx_repositories_project_id ON repositories(project_id);
                CREATE INDEX idx_repositories_github_connection_id ON repositories(github_connection_id);
                CREATE INDEX idx_repositories_github_repo_id ON repositories(github_repo_id);
                
                -- One project can have only one repository linked
                CREATE UNIQUE INDEX idx_repositories_project ON repositories(project_id);
            """))
            connection.commit()
            
            logger.info("✅ Migration: repositories table created successfully")
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
        ("move_review_to_translations", migrate_move_review_to_translations_if_needed),
        ("migrate_to_activity_logs", migrate_to_activity_logs_if_needed),
        ("add_ai_translation_action_type", migrate_add_ai_translation_action_type_if_needed),
        ("create_teams_system", migrate_create_teams_system_if_needed),
        ("add_team_action_types", migrate_add_team_action_types_if_needed),
        ("add_team_id_to_activity_logs", migrate_add_team_id_to_activity_logs_if_needed),
        ("set_default_project_status", migrate_set_default_project_status_if_needed),
        ("add_onboarding_completed", migrate_add_onboarding_completed_if_needed),
        ("create_password_reset_tokens", migrate_create_password_reset_tokens_if_needed),
        ("add_keys_batch_import_action_type", migrate_add_keys_batch_import_action_type_if_needed),
        ("add_is_plural_to_keys", migrate_add_is_plural_to_keys_if_needed),
        ("create_github_connections", migrate_create_github_connections_if_needed),
        ("create_repositories", migrate_create_repositories_if_needed),
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

