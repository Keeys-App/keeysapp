"""
Migration: Add tags support to keys and projects

This migration adds:
- tags field to keys table (JSON array of tag strings)
- available_tags field to projects table (JSON array of available tag strings)
"""

from sqlalchemy import text
import logging
from app.database import engine

logger = logging.getLogger(__name__)


def upgrade():
    """
    Add tags and available_tags columns.
    """
    logger.info("Adding tags support to keys and projects...")
    
    with engine.begin() as connection:
        # Add tags column to keys table
        logger.info("Adding tags column to keys table...")
        connection.execute(text("""
            ALTER TABLE keys 
            ADD COLUMN IF NOT EXISTS tags JSON DEFAULT '[]'::json NOT NULL
        """))
        
        # Add available_tags column to projects table
        logger.info("Adding available_tags column to projects table...")
        connection.execute(text("""
            ALTER TABLE projects 
            ADD COLUMN IF NOT EXISTS available_tags JSON DEFAULT '[]'::json NOT NULL
        """))
        
        logger.info("Tags support added successfully!")


def downgrade():
    """
    Remove tags and available_tags columns.
    """
    logger.info("Removing tags support from keys and projects...")
    
    with engine.begin() as connection:
        # Remove tags column from keys table
        logger.info("Removing tags column from keys table...")
        connection.execute(text("""
            ALTER TABLE keys 
            DROP COLUMN IF EXISTS tags
        """))
        
        # Remove available_tags column from projects table
        logger.info("Removing available_tags column from projects table...")
        connection.execute(text("""
            ALTER TABLE projects 
            DROP COLUMN IF EXISTS available_tags
        """))
        
        logger.info("Tags support removed successfully!")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting migration: add_tags_support")
    upgrade()
    logger.info("Migration completed successfully!")

