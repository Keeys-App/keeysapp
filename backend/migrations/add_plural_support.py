"""
Migration: Add plural support to keys

This migration adds:
- is_plural field to keys table (Boolean, default False)
"""

from sqlalchemy import text
import logging
from app.database import engine

logger = logging.getLogger(__name__)


def upgrade():
    """
    Add is_plural column to keys table.
    """
    logger.info("Adding plural support to keys...")
    
    with engine.begin() as connection:
        # Add is_plural column to keys table
        logger.info("Adding is_plural column to keys table...")
        connection.execute(text("""
            ALTER TABLE keys 
            ADD COLUMN IF NOT EXISTS is_plural BOOLEAN NOT NULL DEFAULT FALSE
        """))
        
        logger.info("Plural support added successfully!")


def downgrade():
    """
    Remove is_plural column from keys table.
    """
    logger.info("Removing plural support from keys...")
    
    with engine.begin() as connection:
        # Remove is_plural column from keys table
        logger.info("Removing is_plural column from keys table...")
        connection.execute(text("""
            ALTER TABLE keys 
            DROP COLUMN IF EXISTS is_plural
        """))
        
        logger.info("Plural support removed successfully!")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting migration: add_plural_support")
    upgrade()
    logger.info("Migration completed successfully!")

