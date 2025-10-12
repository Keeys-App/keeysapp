"""
Migration to assign existing projects without team_id to default teams.
Creates a default team for each user who has projects without team_id.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from app.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """
    Migrate existing projects to teams:
    1. Find all projects without team_id
    2. Group by owner_id
    3. For each owner, create a default team if needed
    4. Assign all their projects to that team
    """
    with engine.connect() as conn:
        logger.info("Starting migration of existing projects to teams...")
        
        # Get all projects without team_id
        result = conn.execute(text("""
            SELECT id, owner_id, name 
            FROM projects 
            WHERE team_id IS NULL
            ORDER BY owner_id
        """))
        projects_without_team = result.fetchall()
        
        if not projects_without_team:
            logger.info("✅ No projects without team_id found. Migration not needed.")
            return
        
        logger.info(f"Found {len(projects_without_team)} projects without team_id")
        
        # Group projects by owner
        projects_by_owner = {}
        for proj_id, owner_id, name in projects_without_team:
            if owner_id not in projects_by_owner:
                projects_by_owner[owner_id] = []
            projects_by_owner[owner_id].append((proj_id, name))
        
        logger.info(f"Found {len(projects_by_owner)} users with projects needing migration")
        
        # For each owner, create or find default team and assign projects
        for owner_id, projects in projects_by_owner.items():
            logger.info(f"\nProcessing owner_id: {owner_id}")
            
            # Check if user already has a team
            result = conn.execute(text("""
                SELECT id, name FROM teams 
                WHERE owner_id = :owner_id 
                ORDER BY created_at 
                LIMIT 1
            """), {"owner_id": owner_id})
            
            existing_team = result.fetchone()
            
            if existing_team:
                team_id = existing_team[0]
                team_name = existing_team[1]
                logger.info(f"  Using existing team: '{team_name}' (ID: {team_id})")
            else:
                # Create a default team for this user
                logger.info(f"  Creating default team for user {owner_id}")
                
                # Get username for better team name
                result = conn.execute(text("""
                    SELECT username FROM users WHERE id = :owner_id
                """), {"owner_id": owner_id})
                user = result.fetchone()
                username = user[0] if user else f"User{owner_id}"
                
                # Create team
                result = conn.execute(text("""
                    INSERT INTO teams (name, description, owner_id)
                    VALUES (:name, :description, :owner_id)
                    RETURNING id
                """), {
                    "name": f"{username}'s Projects",
                    "description": "Default team for existing projects",
                    "owner_id": owner_id
                })
                team_id = result.fetchone()[0]
                conn.commit()
                logger.info(f"  ✓ Created team: '{username}'s Projects' (ID: {team_id})")
            
            # Assign all projects to this team
            for proj_id, proj_name in projects:
                conn.execute(text("""
                    UPDATE projects 
                    SET team_id = :team_id 
                    WHERE id = :proj_id
                """), {"team_id": team_id, "proj_id": proj_id})
                logger.info(f"    ✓ Assigned project '{proj_name}' (ID: {proj_id}) to team {team_id}")
            
            conn.commit()
        
        # Verify migration
        result = conn.execute(text("SELECT COUNT(*) FROM projects WHERE team_id IS NULL"))
        remaining = result.fetchone()[0]
        
        if remaining == 0:
            logger.info("\n✅ Migration completed successfully!")
            logger.info("All projects now have team_id assigned.")
        else:
            logger.warning(f"\n⚠️  Warning: {remaining} projects still without team_id")
        
        # Now we can make team_id NOT NULL and add foreign key
        logger.info("\nAdding NOT NULL constraint and foreign key to projects.team_id...")
        
        try:
            # Add foreign key constraint
            conn.execute(text("""
                ALTER TABLE projects 
                ADD CONSTRAINT projects_team_id_fkey 
                FOREIGN KEY (team_id) 
                REFERENCES teams(id) 
                ON DELETE CASCADE
            """))
            conn.commit()
            logger.info("✓ Added foreign key constraint")
        except Exception as e:
            if "already exists" in str(e):
                logger.info("✓ Foreign key constraint already exists")
            else:
                logger.warning(f"Could not add foreign key: {e}")
        
        try:
            # Make team_id NOT NULL
            conn.execute(text("ALTER TABLE projects ALTER COLUMN team_id SET NOT NULL"))
            conn.commit()
            logger.info("✓ Made team_id NOT NULL")
        except Exception as e:
            if "already" in str(e).lower():
                logger.info("✓ team_id already NOT NULL")
            else:
                logger.warning(f"Could not set NOT NULL: {e}")
        
        logger.info("\n🎉 All done! Projects are now properly assigned to teams.")


if __name__ == "__main__":
    migrate()

