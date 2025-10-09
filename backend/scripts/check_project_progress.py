"""
Script to check translation progress for all projects.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.project import Project
from app.schemas.project import build_project_type


def check_projects():
    """
    Check translation progress for all projects.
    """
    db = SessionLocal()
    
    try:
        projects = db.query(Project).all()
        
        if not projects:
            print("No projects found")
            return
        
        for project in projects:
            print(f"\n{'='*60}")
            print(f"Project: {project.name}")
            print(f"Languages: {project.languages}")
            print(f"Keys count: {len(project.keys)}")
            
            # Calculate what's needed
            keys_count = len(project.keys)
            languages_count = len(project.languages) if project.languages else 0
            total_required = keys_count * languages_count
            
            print(f"\n📊 Expected translations: {keys_count} keys × {languages_count} languages = {total_required}")
            
            # Show each key and its translations
            for key in project.keys:
                print(f"\n  Key: {key.key}")
                print(f"  Translations ({len(key.translations)}/{languages_count}):")
                
                # Show all languages
                for lang in project.languages:
                    trans = next((t for t in key.translations if t.language == lang), None)
                    if trans:
                        value_preview = trans.value[:50] + "..." if len(trans.value) > 50 else trans.value
                        empty_flag = " ⚠️  EMPTY!" if not trans.value.strip() else ""
                        print(f"    ✓ {lang}: '{value_preview}'{empty_flag}")
                    else:
                        print(f"    ✗ {lang}: (missing)")
            
            # Count actual translations
            total_translated = sum(
                1 for key in project.keys 
                for translation in key.translations 
                if translation.value and translation.value.strip()
            )
            
            progress = int((total_translated / total_required) * 100) if total_required > 0 else 0
            
            print(f"\n✅ Filled translations: {total_translated}")
            print(f"📈 Progress: {progress}%")
            
            # Build project type to compare
            project_type = build_project_type(project, project.owner_id)
            print(f"🔍 API returns: {project_type.translation_progress}%")
    
    finally:
        db.close()


if __name__ == "__main__":
    print("Checking project translation progress...\n")
    check_projects()

