"""
Script to check for empty or whitespace-only translations in the database.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.key import Translation, Key
from app.models.project import Project


def check_empty_translations():
    """
    Check for translations with empty or whitespace-only values.
    """
    db = SessionLocal()
    
    try:
        # Find all translations
        all_translations = db.query(Translation).all()
        print(f"Total translations in DB: {len(all_translations)}\n")
        
        # Check for empty or whitespace translations
        empty_translations = []
        for trans in all_translations:
            if not trans.value or not trans.value.strip():
                empty_translations.append(trans)
                key = db.query(Key).filter(Key.id == trans.key_id).first()
                project = db.query(Project).filter(Project.id == key.project_id).first() if key else None
                
                print(f"❌ Empty translation found:")
                print(f"   Project: {project.name if project else 'N/A'}")
                print(f"   Key: {key.key if key else 'N/A'}")
                print(f"   Language: {trans.language}")
                print(f"   Value: '{trans.value}' (length: {len(trans.value)})")
                print()
        
        if not empty_translations:
            print("✅ No empty translations found!")
        else:
            print(f"\n📊 Summary: Found {len(empty_translations)} empty translation(s)")
            
            # Option to delete
            response = input("\nDo you want to delete these empty translations? (yes/no): ")
            if response.lower() == 'yes':
                for trans in empty_translations:
                    db.delete(trans)
                db.commit()
                print(f"✅ Deleted {len(empty_translations)} empty translation(s)")
            else:
                print("Skipped deletion")
    
    finally:
        db.close()


if __name__ == "__main__":
    print("Checking for empty translations...\n")
    check_empty_translations()

