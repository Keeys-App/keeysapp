"""
Migration: Add onboarding_completed field to users table

This migration adds the onboarding_completed boolean field to track
whether a user has completed the initial onboarding wizard.

Usage:
    python -m migrations.add_onboarding_completed
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upgrade():
    """Add onboarding_completed column to users table."""
    logger.info("Starting migration: add_onboarding_completed")
    
    with engine.begin() as conn:
        try:
            # Add onboarding_completed column with default False
            logger.info("Adding onboarding_completed column to users table...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE
            """))
            
            logger.info("✓ Successfully added onboarding_completed column")
            logger.info("Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise


def downgrade():
    """Remove onboarding_completed column from users table."""
    logger.info("Starting downgrade: remove onboarding_completed")
    
    with engine.begin() as conn:
        try:
            logger.info("Removing onboarding_completed column from users table...")
            conn.execute(text("""
                ALTER TABLE users 
                DROP COLUMN IF EXISTS onboarding_completed
            """))
            
            logger.info("✓ Successfully removed onboarding_completed column")
            logger.info("Downgrade completed successfully!")
            
        except Exception as e:
            logger.error(f"Downgrade failed: {e}")
            raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Add onboarding_completed field to users table")
    parser.add_argument(
        "--downgrade",
        action="store_true",
        help="Downgrade (remove the column)"
    )
    
    args = parser.parse_args()
    
    if args.downgrade:
        downgrade()
    else:
        upgrade()

