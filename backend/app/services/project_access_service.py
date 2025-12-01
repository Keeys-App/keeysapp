from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
import logging

from app.models.project_access import ProjectAccess
from app.models.project import Project
from app.models.user import User
from app.models.team import TeamMember
from app.models.activity_log import ActivityLog, ActionType

logger = logging.getLogger(__name__)


class ProjectAccessService:
    """
    Service for managing user access to specific projects.
    """

    @staticmethod
    async def grant_project_access(
        db: AsyncSession,
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
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return None
        
        # Check if granting user has admin access or is owner
        if not await ProjectAccessService._can_manage_project_access(db, project_id, granted_by_user_id):
            return None
        
        # Check if user is in the team
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        
        # Verify user is in team (owner or member)
        is_owner = project.owner_id == user_id
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == project.team_id,
                TeamMember.user_id == user_id
            )
        )
        is_member = result.scalar_one_or_none() is not None
        
        if not is_owner and not is_member:
            logger.warning(f"User {user_id} is not in team {project.team_id}")
            return None
        
        # Check if access already exists
        result = await db.execute(
            select(ProjectAccess).where(
                ProjectAccess.project_id == project_id,
                ProjectAccess.user_id == user_id
            )
        )
        existing_access = result.scalar_one_or_none()
        
        if existing_access:
            # Update role if already exists
            old_role = existing_access.role
            existing_access.role = role
            existing_access.granted_by_user_id = granted_by_user_id
            
            # Log role change if different
            if old_role != role:
                log = ActivityLog(
                    project_id=project_id,
                    user_id=granted_by_user_id,
                    affected_user_id=user_id,
                    action=ActionType.MEMBER_ROLE_CHANGE,
                    field_name="role",
                    old_value=old_role,
                    new_value=role
                )
                db.add(log)
            
            await db.commit()
            await db.refresh(existing_access)
            return existing_access
        
        # Create new access
        access = ProjectAccess(
            project_id=project_id,
            user_id=user_id,
            role=role,
            granted_by_user_id=granted_by_user_id
        )
        db.add(access)
        await db.flush()
        
        # Log member addition
        log = ActivityLog(
            project_id=project_id,
            user_id=granted_by_user_id,
            affected_user_id=user_id,
            action=ActionType.MEMBER_ADD,
            field_name="role",
            new_value=role
        )
        db.add(log)
        
        await db.commit()
        await db.refresh(access)
        return access

    @staticmethod
    async def revoke_project_access(
        db: AsyncSession,
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
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return False
        
        # Check if revoking user has admin access or is owner
        if not await ProjectAccessService._can_manage_project_access(db, project_id, revoked_by_user_id):
            return False
        
        # Cannot revoke owner's access
        if project.owner_id == user_id:
            return False
        
        # Find and remove access
        result = await db.execute(
            select(ProjectAccess).where(
                ProjectAccess.project_id == project_id,
                ProjectAccess.user_id == user_id
            )
        )
        access = result.scalar_one_or_none()
        
        if not access:
            return False
        
        # Log member removal
        log = ActivityLog(
            project_id=project_id,
            user_id=revoked_by_user_id,
            affected_user_id=user_id,
            action=ActionType.MEMBER_REMOVE,
            field_name="role",
            old_value=access.role
        )
        db.add(log)
        
        db.delete(access)
        await db.commit()
        return True

    @staticmethod
    async def update_project_access_role(
        db: AsyncSession,
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
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return None
        
        # Check if updating user has admin access or is owner
        if not await ProjectAccessService._can_manage_project_access(db, project_id, updated_by_user_id):
            return None
        
        # Cannot change owner's role (owner doesn't need ProjectAccess)
        if project.owner_id == user_id:
            return None
        
        # Find and update access
        result = await db.execute(
            select(ProjectAccess).where(
                ProjectAccess.project_id == project_id,
                ProjectAccess.user_id == user_id
            )
        )
        access = result.scalar_one_or_none()
        
        if not access:
            return None
        
        # Log role change if different
        old_role = access.role
        access.role = role
        access.granted_by_user_id = updated_by_user_id
        
        if old_role != role:
            log = ActivityLog(
                project_id=project_id,
                user_id=updated_by_user_id,
                affected_user_id=user_id,
                action=ActionType.MEMBER_ROLE_CHANGE,
                field_name="role",
                old_value=old_role,
                new_value=role
            )
            db.add(log)
        
        await db.commit()
        await db.refresh(access)
        return access

    @staticmethod
    async def get_project_members(db: AsyncSession, project_id: int) -> List[ProjectAccess]:
        """
        Get all users with access to a project.
        
        Args:
            db: Database session
            project_id: Internal project ID
            
        Returns:
            List of ProjectAccess objects with eager loaded users
        """
        result = await db.execute(
            select(ProjectAccess)
            .options(
                joinedload(ProjectAccess.user),
                joinedload(ProjectAccess.granted_by)
            )
            .where(ProjectAccess.project_id == project_id)
        )
        return result.scalars().all()

    @staticmethod
    async def check_project_access(db: AsyncSession, project_id: int, user_id: int) -> bool:
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
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return False
        
        # Owner always has access
        if project.owner_id == user_id:
            return True
        
        # Check ProjectAccess
        result = await db.execute(
            select(ProjectAccess).where(
                ProjectAccess.project_id == project_id,
                ProjectAccess.user_id == user_id
            )
        )
        access = result.scalar_one_or_none()
        
        return access is not None

    @staticmethod
    async def get_user_role_in_project(db: AsyncSession, project_id: int, user_id: int) -> Optional[str]:
        """
        Get user's role in a project.
        
        Args:
            db: Database session
            project_id: Internal project ID
            user_id: User ID
            
        Returns:
            Role string or None if no access
        """
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return None
        
        # Owner has implicit admin role
        if project.owner_id == user_id:
            return "admin"
        
        # Check ProjectAccess
        result = await db.execute(
            select(ProjectAccess).where(
                ProjectAccess.project_id == project_id,
                ProjectAccess.user_id == user_id
            )
        )
        access = result.scalar_one_or_none()
        
        return access.role if access else None

    @staticmethod
    async def get_team_members_with_access(
        db: AsyncSession,
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
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return {}
        
        # Get all team members
        result = await db.execute(
            select(TeamMember).where(TeamMember.team_id == project.team_id)
        )
        team_members = result.scalars().all()
        
        # Get all project access entries
        result = await db.execute(
            select(ProjectAccess).where(ProjectAccess.project_id == project_id)
        )
        project_accesses = result.scalars().all()
        
        # Build result dict
        result_dict = {}
        
        # Add owner with admin role
        result_dict[project.owner_id] = "admin"
        
        # Add all team members
        for member in team_members:
            if member.user_id not in result_dict:
                result_dict[member.user_id] = None
        
        # Update with project access
        for access in project_accesses:
            result_dict[access.user_id] = access.role
        
        return result_dict

    @staticmethod
    async def _can_manage_project_access(db: AsyncSession, project_id: int, user_id: int) -> bool:
        """
        Check if user can manage project access (owner or admin role).
        
        Args:
            db: Database session
            project_id: Internal project ID
            user_id: User ID
            
        Returns:
            True if user can manage, False otherwise
        """
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return False
        
        # Owner can always manage
        if project.owner_id == user_id:
            return True
        
        # Check if user has admin role
        result = await db.execute(
            select(ProjectAccess).where(
                ProjectAccess.project_id == project_id,
                ProjectAccess.user_id == user_id,
                ProjectAccess.role == "admin"
            )
        )
        access = result.scalar_one_or_none()
        
        return access is not None
