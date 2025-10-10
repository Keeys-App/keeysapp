from typing import Optional, List
from sqlalchemy.orm import Session, joinedload, selectinload
import uuid as uuid_lib

from app.models.project import Project, ProjectMember
from app.models.user import User


class ProjectService:
    """
    Service for managing projects and project memberships.
    """

    @staticmethod
    def create_project(
        db: Session,
        owner_id: int,
        name: str,
        description: Optional[str] = None,
        languages: Optional[List[str]] = None,
        default_language: Optional[str] = None,
        color: str = "#6366f1",
        status: str = "active"
    ) -> Project:
        """
        Create a new project.
        
        Args:
            db: Database session
            owner_id: ID of the project owner
            name: Project name
            description: Project description
            languages: List of language codes
            default_language: Default language code (must be in languages list)
            color: Hex color code for the project
            status: Project status (active, archived, draft)
            
        Returns:
            Created project
        """
        if languages is None:
            languages = []
            
        project = Project(
            name=name,
            description=description,
            languages=languages,
            default_language=default_language,
            color=color,
            status=status,
            owner_id=owner_id
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_project_by_public_id(db: Session, public_id: str) -> Optional[Project]:
        """
        Get a project by its public UUID.
        Uses eager loading to prevent N+1 query problems.
        
        Args:
            db: Database session
            public_id: Public UUID of the project
            
        Returns:
            Project or None
        """
        try:
            uuid_obj = uuid_lib.UUID(public_id)
            # Eager load all related data to prevent N+1 queries
            return db.query(Project).options(
                joinedload(Project.owner),
                selectinload(Project.members).joinedload(ProjectMember.user),
                selectinload(Project.keys).selectinload('translations')
            ).filter(Project.public_id == uuid_obj).first()
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def get_user_projects(db: Session, user_id: int) -> List[Project]:
        """
        Get all projects where user is owner or member.
        Uses eager loading to prevent N+1 query problems.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of projects
        """
        # Eager load all related data to prevent N+1 queries
        # Use selectinload for one-to-many relationships to avoid cartesian products
        eager_options = [
            joinedload(Project.owner),  # Load owner (many-to-one)
            selectinload(Project.members).joinedload(ProjectMember.user),  # Load members and their users
            selectinload(Project.keys).selectinload('translations')  # Load keys and their translations
        ]
        
        # Get projects where user is owner
        owned_projects = db.query(Project).options(
            *eager_options
        ).filter(
            Project.owner_id == user_id
        ).all()
        owned_project_ids = {p.id for p in owned_projects}
        
        # Get projects where user is member
        member_projects = db.query(Project).options(
            *eager_options
        ).join(
            ProjectMember, Project.id == ProjectMember.project_id
        ).filter(
            ProjectMember.user_id == user_id
        ).all()
        
        # Combine and deduplicate
        all_projects = owned_projects.copy()
        for project in member_projects:
            if project.id not in owned_project_ids:
                all_projects.append(project)
        
        return all_projects

    @staticmethod
    def update_project(
        db: Session,
        public_id: str,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        languages: Optional[List[str]] = None,
        default_language: Optional[str] = None,
        color: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[Project]:
        """
        Update a project. Only owner or admin members can update.
        
        Args:
            db: Database session
            public_id: Public UUID of the project
            user_id: User ID requesting the update
            name: New project name
            description: New project description
            languages: New list of language codes
            default_language: New default language code
            color: New hex color code
            status: New project status
            
        Returns:
            Updated project or None if not found or no permission
        """
        project = ProjectService.get_project_by_public_id(db, public_id)
        if not project:
            return None
        
        # Check if user has permission to update
        if not ProjectService.can_user_edit_project(db, project.id, user_id):
            return None
        
        # Update fields if provided
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if languages is not None:
            project.languages = languages
        if default_language is not None:
            project.default_language = default_language
        if color is not None:
            project.color = color
        if status is not None:
            project.status = status
        
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(db: Session, public_id: str, user_id: int) -> bool:
        """
        Delete a project. Only owner can delete.
        
        Args:
            db: Database session
            public_id: Public UUID of the project
            user_id: User ID requesting the deletion
            
        Returns:
            True if deleted, False otherwise
        """
        project = ProjectService.get_project_by_public_id(db, public_id)
        if not project:
            return False
        
        # Only owner can delete
        if project.owner_id != user_id:
            return False
        
        db.delete(project)
        db.commit()
        return True

    @staticmethod
    def check_project_access(db: Session, project_id: int, user_id: int) -> bool:
        """
        Check if user has access to a project (owner or member).
        
        Args:
            db: Database session
            project_id: Internal project ID
            user_id: User ID
            
        Returns:
            True if user has access, False otherwise
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return False
        
        # Check if owner
        if project.owner_id == user_id:
            return True
        
        # Check if member
        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        ).first()
        
        return member is not None

    @staticmethod
    def can_user_edit_project(db: Session, project_id: int, user_id: int) -> bool:
        """
        Check if user can edit a project (owner or admin member).
        
        Args:
            db: Database session
            project_id: Internal project ID
            user_id: User ID
            
        Returns:
            True if user can edit, False otherwise
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return False
        
        # Owner can always edit
        if project.owner_id == user_id:
            return True
        
        # Check if admin member
        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            ProjectMember.role == "admin"
        ).first()
        
        return member is not None

    @staticmethod
    def add_project_member(
        db: Session,
        project_public_id: str,
        user_public_id: str,
        role: str,
        added_by_user_id: int
    ) -> Optional[ProjectMember]:
        """
        Add a member to a project. Only owner or admin can add members.
        
        Args:
            db: Database session
            project_public_id: Public UUID of the project
            user_public_id: Public UUID of the user to add
            role: Role for the new member (admin, editor, viewer)
            added_by_user_id: User ID who is adding the member
            
        Returns:
            Created ProjectMember or None if failed
        """
        # Get project
        project = ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return None
        
        # Check permission
        if not ProjectService.can_user_edit_project(db, project.id, added_by_user_id):
            return None
        
        # Get user to add
        try:
            uuid_obj = uuid_lib.UUID(user_public_id)
            user = db.query(User).filter(User.public_id == uuid_obj).first()
            if not user:
                return None
        except (ValueError, AttributeError):
            return None
        
        # Check if already a member
        existing_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == user.id
        ).first()
        
        if existing_member:
            # Update role if already exists
            existing_member.role = role
            db.commit()
            db.refresh(existing_member)
            return existing_member
        
        # Create new member
        member = ProjectMember(
            project_id=project.id,
            user_id=user.id,
            role=role
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def remove_project_member(
        db: Session,
        project_public_id: str,
        user_public_id: str,
        removed_by_user_id: int
    ) -> bool:
        """
        Remove a member from a project. Only owner or admin can remove members.
        
        Args:
            db: Database session
            project_public_id: Public UUID of the project
            user_public_id: Public UUID of the user to remove
            removed_by_user_id: User ID who is removing the member
            
        Returns:
            True if removed, False otherwise
        """
        # Get project
        project = ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return False
        
        # Check permission
        if not ProjectService.can_user_edit_project(db, project.id, removed_by_user_id):
            return False
        
        # Get user to remove
        try:
            uuid_obj = uuid_lib.UUID(user_public_id)
            user = db.query(User).filter(User.public_id == uuid_obj).first()
            if not user:
                return False
        except (ValueError, AttributeError):
            return False
        
        # Cannot remove owner
        if project.owner_id == user.id:
            return False
        
        # Find and remove member
        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == user.id
        ).first()
        
        if not member:
            return False
        
        db.delete(member)
        db.commit()
        return True

