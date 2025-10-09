#!/usr/bin/env python3
"""
Script to create projects and project_members tables.
This migration adds project management functionality.
"""
from sqlalchemy import text
from app.database import engine
from app.models.base import Base
from app.models.user import User
from app.models.project import Project, ProjectMember


def create_projects_tables():
    """
    Create projects and project_members tables if they don't exist.
    """
    print("📝 Creating projects tables...")
    
    # Import all models to register them with Base
    # This ensures the metadata knows about all tables
    
    try:
        # Create only the projects tables
        # Using checkfirst=True to avoid errors if tables already exist
        Project.__table__.create(bind=engine, checkfirst=True)
        print("✅ Projects table created")
        
        ProjectMember.__table__.create(bind=engine, checkfirst=True)
        print("✅ Project_members table created")
        
        print("")
        print("🎉 Projects tables created successfully!")
        print("   Tables created:")
        print("   - projects (id, public_id, name, description, languages, color, status, owner_id, timestamps)")
        print("   - project_members (id, project_id, user_id, role, created_at)")
        print("")
        print("You can now start creating projects.")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        print("Note: If tables already exist, this is expected behavior.")
        return False
    
    return True


def check_tables_exist():
    """
    Check if projects tables already exist.
    """
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'projects')"
        ))
        projects_exists = result.scalar()
        
        result = conn.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'project_members')"
        ))
        members_exists = result.scalar()
        
        return projects_exists, members_exists


if __name__ == "__main__":
    print("")
    print("=" * 60)
    print("  CREATE PROJECTS TABLES MIGRATION")
    print("=" * 60)
    print("")
    
    # Check if tables exist
    try:
        projects_exists, members_exists = check_tables_exist()
        
        if projects_exists and members_exists:
            print("ℹ️  Projects tables already exist.")
            response = input("Do you want to recreate them? This will DELETE ALL PROJECTS DATA! (yes/no): ")
            
            if response.lower() == 'yes':
                print("Dropping existing tables...")
                with engine.connect() as conn:
                    conn.execute(text("DROP TABLE IF EXISTS project_members CASCADE"))
                    conn.execute(text("DROP TABLE IF EXISTS projects CASCADE"))
                    conn.commit()
                print("✅ Existing tables dropped")
            else:
                print("Operation cancelled. No changes made.")
                exit(0)
    except Exception as e:
        print(f"ℹ️  Could not check for existing tables (tables likely don't exist yet): {e}")
        print("Proceeding with table creation...")
    
    print("")
    create_projects_tables()

