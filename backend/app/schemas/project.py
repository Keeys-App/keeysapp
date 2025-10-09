import strawberry
from typing import Optional, List
from datetime import datetime
from strawberry.types import Info
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
import logging

from app.database import get_db
from app.services.project_service import ProjectService
from app.services.user_service import UserService
from app.core.security import decode_access_token
from app.core.exceptions import (
    AuthenticationError,
    UnauthorizedError,
    DatabaseError,
    handle_database_exception
)
from app.schemas.auth import UserType

logger = logging.getLogger(__name__)


@strawberry.type
class ProjectMemberType:
    """
    GraphQL type for ProjectMember.
    """
    user: UserType
    role: str
    created_at: datetime


@strawberry.type
class ProjectType:
    """
    GraphQL type for Project.
    Uses public_id (UUID) instead of internal ID for security.
    """
    id: str  # UUID as string for public API
    name: str
    description: Optional[str]
    languages: List[str]
    color: str
    status: str
    owner: UserType
    members: List[ProjectMemberType]
    can_edit: bool
    created_at: datetime
    updated_at: Optional[datetime]


@strawberry.input
class CreateProjectInput:
    """
    Input type for creating a project.
    """
    name: str
    description: Optional[str] = None
    languages: Optional[List[str]] = None
    color: Optional[str] = "#6366f1"
    status: Optional[str] = "active"


@strawberry.input
class UpdateProjectInput:
    """
    Input type for updating a project.
    """
    id: str  # UUID
    name: Optional[str] = None
    description: Optional[str] = None
    languages: Optional[List[str]] = None
    color: Optional[str] = None
    status: Optional[str] = None


@strawberry.input
class AddProjectMemberInput:
    """
    Input type for adding a member to a project.
    """
    project_id: str  # UUID
    user_id: str  # UUID
    role: str  # admin, editor, viewer


def get_current_user_id(info: Info) -> Optional[int]:
    """
    Helper function to get current user ID from request context.
    
    Args:
        info: GraphQL info object
        
    Returns:
        User ID or None
    """
    try:
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
        
        db: Session = next(get_db())
        try:
            user = UserService.get_user_by_public_id(db, public_id)
            if not user:
                logger.warning(f"User not found for public_id")
                return None
            return user.id
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error getting current user: {type(e).__name__}: {str(e)}")
        return None


def build_project_type(project, current_user_id: int) -> ProjectType:
    """
    Build ProjectType from Project model.
    
    Args:
        project: Project model instance
        current_user_id: Current user's ID
        
    Returns:
        ProjectType
    """
    # Build owner
    owner = UserType(
        id=str(project.owner.public_id),
        email=project.owner.email,
        username=project.owner.username,
        is_active=project.owner.is_active,
        is_superuser=project.owner.is_superuser
    )
    
    # Build members
    members = []
    for member in project.members:
        members.append(ProjectMemberType(
            user=UserType(
                id=str(member.user.public_id),
                email=member.user.email,
                username=member.user.username,
                is_active=member.user.is_active,
                is_superuser=member.user.is_superuser
            ),
            role=member.role,
            created_at=member.created_at
        ))
    
    # Check if current user can edit
    can_edit = project.owner_id == current_user_id
    if not can_edit:
        for member in project.members:
            if member.user_id == current_user_id and member.role == "admin":
                can_edit = True
                break
    
    return ProjectType(
        id=str(project.public_id),
        name=project.name,
        description=project.description,
        languages=project.languages or [],
        color=project.color,
        status=project.status,
        owner=owner,
        members=members,
        can_edit=can_edit,
        created_at=project.created_at,
        updated_at=project.updated_at
    )


@strawberry.type
class ProjectQuery:
    """
    GraphQL queries for projects.
    """

    @strawberry.field
    def projects(self, info: Info) -> List[ProjectType]:
        """
        Get all projects for current user (owned or member).
        
        Args:
            info: GraphQL info object
            
        Returns:
            List of projects
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        from app.core.exceptions import UnauthorizedError
        
        try:
            current_user_id = get_current_user_id(info)
            if not current_user_id:
                raise UnauthorizedError("Authentication required to access projects")
            
            db: Session = next(get_db())
            try:
                projects = ProjectService.get_user_projects(db, current_user_id)
                return [build_project_type(project, current_user_id) for project in projects]
            finally:
                db.close()
        except UnauthorizedError:
            # Re-raise authentication errors
            raise
        except Exception as e:
            logger.error(f"Error in projects query: {type(e).__name__}: {str(e)}")
            return []

    @strawberry.field
    def project(self, info: Info, id: str) -> Optional[ProjectType]:
        """
        Get a specific project by ID.
        
        Args:
            info: GraphQL info object
            id: Project UUID
            
        Returns:
            Project or None
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        try:
            current_user_id = get_current_user_id(info)
            if not current_user_id:
                return None
            
            db: Session = next(get_db())
            try:
                project = ProjectService.get_project_by_public_id(db, id)
                if not project:
                    return None
                
                # Check access
                if not ProjectService.check_project_access(db, project.id, current_user_id):
                    return None
                
                return build_project_type(project, current_user_id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in project query: {type(e).__name__}: {str(e)}")
            return None


@strawberry.type
class ProjectMutation:
    """
    GraphQL mutations for projects.
    """

    @strawberry.mutation
    def create_project(self, input: CreateProjectInput, info: Info) -> ProjectType:
        """
        Create a new project.
        
        Args:
            input: Project creation input
            info: GraphQL info object
            
        Returns:
            Created project
            
        Raises:
            UnauthorizedError: If user is not authenticated
            DatabaseError: If database operation fails
        """
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to create projects")
        
        db: Session = next(get_db())
        
        try:
            project = ProjectService.create_project(
                db=db,
                owner_id=current_user_id,
                name=input.name,
                description=input.description,
                languages=input.languages or [],
                color=input.color or "#6366f1",
                status=input.status or "active"
            )
            
            return build_project_type(project, current_user_id)
        except (UnauthorizedError, AuthenticationError):
            raise
        except (IntegrityError, OperationalError) as e:
            handle_database_exception(e, "project creation")
        except Exception as e:
            handle_database_exception(e, "project creation")
        finally:
            db.close()

    @strawberry.mutation
    def update_project(self, input: UpdateProjectInput, info: Info) -> Optional[ProjectType]:
        """
        Update an existing project.
        
        Args:
            input: Project update input
            info: GraphQL info object
            
        Returns:
            Updated project or None
            
        Raises:
            UnauthorizedError: If user is not authenticated
            DatabaseError: If database operation fails
        """
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to update projects")
        
        db: Session = next(get_db())
        
        try:
            project = ProjectService.update_project(
                db=db,
                public_id=input.id,
                user_id=current_user_id,
                name=input.name,
                description=input.description,
                languages=input.languages,
                color=input.color,
                status=input.status
            )
            
            if not project:
                return None
            
            return build_project_type(project, current_user_id)
        except (UnauthorizedError, AuthenticationError):
            raise
        except (IntegrityError, OperationalError) as e:
            handle_database_exception(e, "project update")
        except Exception as e:
            handle_database_exception(e, "project update")
        finally:
            db.close()

    @strawberry.mutation
    def delete_project(self, id: str, info: Info) -> bool:
        """
        Delete a project.
        
        Args:
            id: Project UUID
            info: GraphQL info object
            
        Returns:
            True if deleted, False otherwise
            
        Raises:
            UnauthorizedError: If user is not authenticated
            DatabaseError: If database operation fails
        """
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to delete projects")
        
        db: Session = next(get_db())
        
        try:
            return ProjectService.delete_project(db, id, current_user_id)
        except (UnauthorizedError, AuthenticationError):
            raise
        except (IntegrityError, OperationalError) as e:
            handle_database_exception(e, "project deletion")
        except Exception as e:
            handle_database_exception(e, "project deletion")
        finally:
            db.close()

    @strawberry.mutation
    def add_project_member(self, input: AddProjectMemberInput, info: Info) -> Optional[ProjectType]:
        """
        Add a member to a project.
        
        Args:
            input: Add member input
            info: GraphQL info object
            
        Returns:
            Updated project or None
            
        Raises:
            UnauthorizedError: If user is not authenticated
            DatabaseError: If database operation fails
        """
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to add project members")
        
        db: Session = next(get_db())
        
        try:
            member = ProjectService.add_project_member(
                db=db,
                project_public_id=input.project_id,
                user_public_id=input.user_id,
                role=input.role,
                added_by_user_id=current_user_id
            )
            
            if not member:
                return None
            
            # Get updated project
            from app.models.project import Project as ProjectModel
            project = db.query(ProjectModel).filter_by(id=member.project_id).first()
            
            if not project:
                return None
            
            return build_project_type(project, current_user_id)
        except (UnauthorizedError, AuthenticationError):
            raise
        except (IntegrityError, OperationalError) as e:
            handle_database_exception(e, "adding project member")
        except Exception as e:
            handle_database_exception(e, "adding project member")
        finally:
            db.close()

