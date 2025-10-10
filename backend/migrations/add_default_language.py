"""
Migration to add default_language column to projects table.
"""

from sqlalchemy import text
from app.database import engine


def upgrade():
    """
    Add default_language column to projects table.
    """
    with engine.connect() as connection:
        # Add default_language column
        connection.execute(
            text("""
                ALTER TABLE projects
                ADD COLUMN IF NOT EXISTS default_language VARCHAR(10);
            """)
        )
        connection.commit()
        print("✅ Successfully added default_language column to projects table")


def downgrade():
    """
    Remove default_language column from projects table.
    """
    with engine.connect() as connection:
        connection.execute(
            text("""
                ALTER TABLE projects
                DROP COLUMN IF EXISTS default_language;
            """)
        )
        connection.commit()
        print("✅ Successfully removed default_language column from projects table")


if __name__ == "__main__":
    print("Running migration: add_default_language")
    upgrade()
    print("Migration completed!")

