from typing import Optional, List, Dict
from sqlalchemy.orm import Session, joinedload
import logging

from app.models.project_access import ProjectAccess
from app.models.project import Project
from app.models.user import User
from app.models.team import TeamMember

logger = logging.getLogger(__name__)


class ProjectAccessService:
    """
    Service for managing user access to specific projects.
    """

    @staticmethod
    def grant_project_access(
        db: Session,
        project_id: int,
        user_id: int,
        role: str,
        granted_by_user_id: int
    ) -> Optional[ProjectAccess]:
        """
        Grant a user access to a project.
        
        Args:
            db: Database session
            project_id: Internal project ID
            user_id: User ID to grant access to
            role: Role for the user (admin, editor, viewer, translator, reviewer)
            granted_by_user_id: User ID who is granting access
            
        Returns:
            Created ProjectAccess or None if failed
        """
        # Check if project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        
        # Check if granting user has admin access or is owner
        if not ProjectAccessService._can_manage_project_access(db, project_id, granted_by_user_id):
            return None
        
        # Check if user is in the team
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Verify user is in team (owner or member)
        is_owner = project.owner_id == user_id
        is_member = db.query(TeamMember).filter(
            TeamMember.team_id == project.team_id,
            TeamMember.user_id == user_id
        ).first() is not None
        
        if not is_owner and not is_member:
            logger.warning(f"User {user_id} is not in team {project.team_id}")
            return None
        
        # Check if access already exists
        existing_access = db.query(ProjectAccess).filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == user_id
        ).first()
        
        if existing_access:
            # Update role if already exists
            existing_access.role = role
            existing_access.granted_by_user_id = granted_by_user_id
            db.commit()
            db.refresh(existing_access)
            return existing_access
        
        # Create new access
        access = ProjectAccess(
            project_id=project_id,
            user_id=user_id,
            role=role,
            granted_by_user_id=granted_by_user_id
        )
        db.add(access)
        db.commit()
        db.refresh(access)
        return access

    @staticmethod
    def revoke_project_access(
        db: Session,
        project_id: int,
        user_id: int,
        revoked_by_user_id: int
    ) -> bool:
        """
        Revoke a user's access to a project.
        
        Args:
            db: Database session
            project_id: Internal project ID
            user_id: User ID to revoke access from
            revoked_by_user_id: User ID who is revoking access
            
        Returns:
            True if revoked, False otherwise
        """
        # Check if project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return False
        
        # Check if revoking user has admin access or is owner
        if not ProjectAccessService._can_manage_project_access(db, project_id, revoked_by_user_id):
            return False
        
        # Cannot revoke owner's access
        if project.owner_id == user_id:
            return False
        
        # Find and remove access
        access = db.query(ProjectAccess).filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == user_id
        ).first()
        
        if not access:
            return False
        
        db.delete(access)
        db.commit()
        return True

    @staticmethod
    def update_project_access_role(
        db: Session,
        project_id: int,
        user_id: int,
        role: str,
        updated_by_user_id: int
    ) -> Optional[ProjectAccess]:
        """
        Update a user's role in a project.
        
        Args:
            db: Database session
            project_id: Internal project ID
            user_id: User ID to update
            role: New role (admin, editor, viewer, translator, reviewer)
            updated_by_user_id: User ID who is updating the role
            
        Returns:
            Updated ProjectAccess or None if failed
        """
        # Check if project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        
        # Check if updating user has admin access or is owner
        if not ProjectAccessService._can_manage_project_access(db, project_id, updated_by_user_id):
            return None
        
        # Cannot change owner's role (owner doesn't need ProjectAccess)
        if project.owner_id == user_id:
            return None
        
        # Find and update access
        access = db.query(ProjectAccess).filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == user_id
        ).first()
        
        if not access:
            return None
        
        access.role = role
        access.granted_by_user_id = updated_by_user_id
        db.commit()
        db.refresh(access)
        return access

    @staticmethod
    def get_project_members(db: Session, project_id: int) -> List[ProjectAccess]:
        """
        Get all users with access to a project.
        
        Args:
            db: Database session
            project_id: Internal project ID
            
        Returns:
            List of ProjectAccess objects with eager loaded users
        """
        return db.query(ProjectAccess).options(
            joinedload(ProjectAccess.user),
            joinedload(ProjectAccess.granted_by)
        ).filter(
            ProjectAccess.project_id == project_id
        ).all()

    @staticmethod
    def check_project_access(db: Session, project_id: int, user_id: int) -> bool:
        """
        Check if user has access to a project.
        Owner always has access, others need ProjectAccess entry.
        
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
        
        # Owner always has access
        if project.owner_id == user_id:
            return True
        
        # Check ProjectAccess
        access = db.query(ProjectAccess).filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == user_id
        ).first()
        
        return access is not None

    @staticmethod
    def get_user_role_in_project(db: Session, project_id: int, user_id: int) -> Optional[str]:
        """
        Get user's role in a project.
        
        Args:
            db: Database session
            project_id: Internal project ID
            user_id: User ID
            
        Returns:
            Role string or None if no access
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        
        # Owner has implicit admin role
        if project.owner_id == user_id:
            return "admin"
        
        # Check ProjectAccess
        access = db.query(ProjectAccess).filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == user_id
        ).first()
        
        return access.role if access else None

    @staticmethod
    def get_team_members_with_access(
        db: Session,
        project_id: int
    ) -> Dict[int, Optional[str]]:
        """
        Get all team members and their access to the project.
        Returns a dict mapping user_id to role (or None if no access).
        
        Args:
            db: Database session
            project_id: Internal project ID
            
        Returns:
            Dict mapping user_id to role (or None)
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {}
        
        # Get all team members
        team_members = db.query(TeamMember).filter(
            TeamMember.team_id == project.team_id
        ).all()
        
        # Get all project access entries
        project_accesses = db.query(ProjectAccess).filter(
            ProjectAccess.project_id == project_id
        ).all()
        
        # Build result dict
        result = {}
        
        # Add owner with admin role
        result[project.owner_id] = "admin"
        
        # Add all team members
        for member in team_members:
            if member.user_id not in result:
                result[member.user_id] = None
        
        # Update with project access
        for access in project_accesses:
            result[access.user_id] = access.role
        
        return result

    @staticmethod
    def _can_manage_project_access(db: Session, project_id: int, user_id: int) -> bool:
        """
        Check if user can manage project access (owner or admin role).
        
        Args:
            db: Database session
            project_id: Internal project ID
            user_id: User ID
            
        Returns:
            True if user can manage, False otherwise
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return False
        
        # Owner can always manage
        if project.owner_id == user_id:
            return True
        
        # Check if user has admin role
        access = db.query(ProjectAccess).filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == user_id,
            ProjectAccess.role == "admin"
        ).first()
        
        return access is not None

