"""
Migration to convert languages from array of strings to array of objects.
Converts ["en", "ru"] to [{"code": "en", "locale": "en-US"}, {"code": "ru", "locale": "ru-RU"}]
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.database import get_db
from app.models.project import Project
from app.constants.languages import DEFAULT_LANGUAGE_LOCALES


def convert_languages_to_config(language_codes: list) -> list:
    """
    Convert list of language codes to list of language config objects.
    
    Args:
        language_codes: List of language codes like ["en", "ru"]
        
    Returns:
        List of language config objects like [{"code": "en", "locale": "en-US"}, ...]
    """
    result = []
    for code in language_codes:
        if isinstance(code, str):
            # It's an old format string code
            locale = DEFAULT_LANGUAGE_LOCALES.get(code, f'{code}-{code.upper()}')
            result.append({
                'code': code,
                'locale': locale
            })
        elif isinstance(code, dict) and 'code' in code and 'locale' in code:
            # It's already in new format
            result.append(code)
    return result


def migrate():
    """
    Migrate all projects to use new language config format.
    """
    print("Starting languages migration...")
    
    db = next(get_db())
    try:
        # Get all projects
        projects = db.query(Project).all()
        print(f"Found {len(projects)} projects to migrate")
        
        migrated_count = 0
        skipped_count = 0
        
        for project in projects:
            if not project.languages:
                print(f"Project {project.id} ({project.name}): No languages, skipping")
                skipped_count += 1
                continue
            
            # Check if already in new format
            needs_migration = False
            for lang in project.languages:
                if isinstance(lang, str):
                    needs_migration = True
                    break
            
            if not needs_migration:
                print(f"Project {project.id} ({project.name}): Already in new format, skipping")
                skipped_count += 1
                continue
            
            # Convert to new format
            old_languages = project.languages.copy()
            new_languages = convert_languages_to_config(project.languages)
            
            project.languages = new_languages
            print(f"Project {project.id} ({project.name}): Migrated {old_languages} -> {new_languages}")
            migrated_count += 1
        
        # Commit all changes
        db.commit()
        
        print(f"\nMigration completed!")
        print(f"Migrated: {migrated_count} projects")
        print(f"Skipped: {skipped_count} projects")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()

