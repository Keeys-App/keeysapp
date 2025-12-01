import strawberry
from typing import Optional, List
from datetime import datetime
from strawberry.types import Info
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, OperationalError
import logging

from app.database import AsyncSessionLocal
from app.services.project_access_service import ProjectAccessService
from app.services.project_service import ProjectService
from app.core.exceptions import (
    UnauthorizedError,
    handle_database_exception
)
from app.schemas.auth import UserType

logger = logging.getLogger(__name__)


@strawberry.type
class ProjectAccessType:
    """
    GraphQL type for ProjectAccess.
    """
    user: UserType
    role: str
    granted_by: Optional[UserType]
    created_at: datetime


@strawberry.input
class GrantProjectAccessInput:
    """
    Input type for granting access to a project.
    """
    project_id: str  # UUID
    user_id: str  # UUID
    role: str  # admin, editor, viewer, translator, reviewer


@strawberry.input
class RevokeProjectAccessInput:
    """
    Input type for revoking access from a project.
    """
    project_id: str  # UUID
    user_id: str  # UUID


@strawberry.input
class UpdateProjectAccessRoleInput:
    """
    Input type for updating a user's role in a project.
    """
    project_id: str  # UUID
    user_id: str  # UUID
    role: str  # admin, editor, viewer, translator, reviewer


async def get_current_user_id(info: Info) -> Optional[int]:
    """
    Helper function to get current user ID from request context.
    
    Args:
        info: GraphQL info object
        
    Returns:
        User ID or None
    """
    try:
        from app.core.security import decode_access_token
        from app.services.user_service import UserService
        
        request = info.context.get("request")
        if not request:
            logger.warning("No request in GraphQL context")
            return None
        
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.warning("No Authorization header in request")
            return None
            
        if not auth_header.startswith("Bearer "):
            logger.warning(f"Invalid Authorization header format")
            return None
        
        token = auth_header.replace("Bearer ", "")
        payload = decode_access_token(token)
        
        if not payload:
            logger.warning("Failed to decode access token")
            return None
        
        public_id = payload.get("sub")
        if not public_id:
            logger.warning("No 'sub' field in token payload")
            return None
        
        async with AsyncSessionLocal() as db:
            user = await UserService.get_user_by_public_id(db, public_id)
            if not user:
                logger.warning(f"User not found for public_id")
                return None
            return user.id
    except Exception as e:
        logger.error(f"Error getting current user: {type(e).__name__}: {str(e)}")
        return None


@strawberry.type
class ProjectAccessMutation:
    """
    GraphQL mutations for project access.
    """

    @strawberry.mutation
    async def grant_project_access(self, input: GrantProjectAccessInput, info: Info) -> bool:
        """
        Grant a user access to a project.
        
        Args:
            input: Grant access input
            info: GraphQL info object
            
        Returns:
            True if granted, False otherwise
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        from app.services.user_service import UserService
        
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to grant project access")
        
        async with AsyncSessionLocal() as db:
            try:
                # Get project by public_id
                project = await ProjectService.get_project_by_public_id(db, input.project_id)
                if not project:
                    return False
                
                # Get user by public_id
                user = await UserService.get_user_by_public_id(db, input.user_id)
                if not user:
                    return False
                
                # Grant access
                access = await ProjectAccessService.grant_project_access(
                    db=db,
                    project_id=project.id,
                    user_id=user.id,
                    role=input.role,
                    granted_by_user_id=current_user_id
                )
                
                return access is not None
            except (UnauthorizedError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "granting project access")
            except Exception as e:
                handle_database_exception(e, "granting project access")

    @strawberry.mutation
    async def revoke_project_access(self, input: RevokeProjectAccessInput, info: Info) -> bool:
        """
        Revoke a user's access to a project.
        
        Args:
            input: Revoke access input
            info: GraphQL info object
            
        Returns:
            True if revoked, False otherwise
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        from app.services.user_service import UserService
        
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to revoke project access")
        
        async with AsyncSessionLocal() as db:
            try:
                # Get project by public_id
                project = await ProjectService.get_project_by_public_id(db, input.project_id)
                if not project:
                    return False
                
                # Get user by public_id
                user = await UserService.get_user_by_public_id(db, input.user_id)
                if not user:
                    return False
                
                # Revoke access
                return await ProjectAccessService.revoke_project_access(
                    db=db,
                    project_id=project.id,
                    user_id=user.id,
                    revoked_by_user_id=current_user_id
                )
            except (UnauthorizedError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "revoking project access")
            except Exception as e:
                handle_database_exception(e, "revoking project access")

    @strawberry.mutation
    async def update_project_access_role(self, input: UpdateProjectAccessRoleInput, info: Info) -> bool:
        """
        Update a user's role in a project.
        
        Args:
            input: Update role input
            info: GraphQL info object
            
        Returns:
            True if updated, False otherwise
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        from app.services.user_service import UserService
        
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to update project access")
        
        async with AsyncSessionLocal() as db:
            try:
                # Get project by public_id
                project = await ProjectService.get_project_by_public_id(db, input.project_id)
                if not project:
                    return False
                
                # Get user by public_id
                user = await UserService.get_user_by_public_id(db, input.user_id)
                if not user:
                    return False
                
                # Update role
                access = await ProjectAccessService.update_project_access_role(
                    db=db,
                    project_id=project.id,
                    user_id=user.id,
                    role=input.role,
                    updated_by_user_id=current_user_id
                )
                
                return access is not None
            except (UnauthorizedError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "updating project access role")
            except Exception as e:
                handle_database_exception(e, "updating project access role")
