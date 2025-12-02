import strawberry
from typing import Optional, List
from datetime import datetime
from strawberry.types import Info
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
import logging

from app.database import AsyncSessionLocal
from app.services.project_service import ProjectService
from app.services.user_service import UserService
from app.core.security import decode_access_token
from app.core.exceptions import (
    AuthenticationError,
    UnauthorizedError,
    handle_database_exception
)
from app.schemas.auth import UserType
from app.constants.languages import LANGUAGE_CONFIGS, get_plural_forms, get_all_languages

logger = logging.getLogger(__name__)


@strawberry.type
class LanguageConfigType:
    """
    GraphQL type for language configuration with custom locale, text direction, and plural forms.
    
    Plural forms follow CLDR standard:
    - zero: Used for zero quantity (e.g., Arabic)
    - one: Singular form (e.g., 1 item)
    - two: Dual form (e.g., Arabic for exactly 2)
    - few: Paucal form (e.g., Russian 2-4)
    - many: Large quantity form (e.g., Russian 5-20)
    - other: General/default form (always present)
    """
    code: str
    locale: str
    direction: str
    plural_forms: List[str]  # CLDR plural forms: ['one', 'other'], ['one', 'few', 'many', 'other'], etc.
    default: bool = False


@strawberry.type
class LanguageProgressType:
    """
    GraphQL type for language translation progress.
    """
    code: str
    progress: int  # Percentage (0-100)
    completed: int  # Number of completed translations
    total: int  # Total number of keys


@strawberry.type
class DetectionPatternsType:
    """
    GraphQL type for language detection patterns (regex strings for file import).
    """
    end_patterns: List[str]      # e.g., app-en.json
    middle_patterns: List[str]   # e.g., en-US.json
    start_patterns: List[str]    # e.g., en.translations.json
    full_names: List[str]        # e.g., english.json


@strawberry.type
class AvailableLanguageType:
    """
    GraphQL type for available language with full metadata.
    Single source of truth for language configuration.
    """
    code: str
    name: str
    native_name: str
    flag: str
    locale: str
    direction: str
    plural_forms: List[str]
    detection_patterns: DetectionPatternsType


@strawberry.input
class LanguageConfigInput:
    """
    Input type for language configuration.
    """
    code: str
    locale: str
    direction: str = 'ltr'


@strawberry.type
class ProjectMemberType:
    """
    GraphQL type for ProjectMember.
    """
    user: UserType
    role: str
    created_at: datetime


@strawberry.type
class SimpleTeamType:
    """
    Simplified GraphQL type for Team (to avoid circular imports).
    """
    id: str  # UUID as string
    name: str
    description: Optional[str]


@strawberry.type
class ProjectType:
    """
    GraphQL type for Project.
    Uses public_id (UUID) instead of internal ID for security.
    """
    id: str  # UUID as string for public API
    name: str
    description: Optional[str]
    languages: List[LanguageConfigType]
    default_language: Optional[str]
    available_tags: List[str]
    color: str
    status: str
    team: SimpleTeamType
    owner: UserType
    access_members: List[ProjectMemberType]  # Users with access to this project
    can_edit: bool
    keys_count: int
    translation_progress: int  # Percentage of completed translations (0-100)
    language_progress: List[LanguageProgressType]  # Progress per language
    created_at: datetime
    updated_at: Optional[datetime]


@strawberry.input
class CreateProjectInput:
    """
    Input type for creating a project.
    """
    name: str
    team_id: str  # UUID of the team this project belongs to
    description: Optional[str] = None
    languages: Optional[List[LanguageConfigInput]] = None
    default_language: Optional[str] = None
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
    languages: Optional[List[LanguageConfigInput]] = None
    default_language: Optional[str] = None
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


async def get_current_user_id(info: Info) -> Optional[int]:
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
        
        async with AsyncSessionLocal() as db:
            user = await UserService.get_user_by_public_id(db, public_id)
            if not user:
                logger.warning(f"User not found for public_id")
                return None
            return user.id
    except Exception as e:
        logger.error(f"Error getting current user: {type(e).__name__}: {str(e)}")
        return None


async def build_project_type(project, current_user_id: int, stats: Optional[dict] = None, db: Optional[AsyncSession] = None) -> Optional[ProjectType]:
    """
    Build ProjectType from Project model.
    
    Args:
        project: Project model instance
        current_user_id: Current user's ID
        stats: Optional dictionary with 'keys_count' and 'translations_count' from SQL
        db: Optional database session for fetching language progress
        
    Returns:
        ProjectType or None if required relations are missing
    """
    # Check required relationships
    if not project.owner or not project.team:
        logger.warning(f"Project {project.id} has missing owner or team relationship")
        return None
    
    # Build owner
    owner = UserType(
        id=str(project.owner.public_id),
        email=project.owner.email,
        username=project.owner.username,
        is_active=project.owner.is_active,
        is_superuser=project.owner.is_superuser,
        onboarding_completed=project.owner.onboarding_completed
    )
    
    # Build team
    team = SimpleTeamType(
        id=str(project.team.public_id),
        name=project.team.name,
        description=project.team.description
    )
    
    # Build access members
    access_members = []
    for access in project.access_members:
        # Skip if user relationship is missing
        if not access.user:
            logger.warning(f"ProjectAccess {access.id} has missing user relationship")
            continue
            
        access_members.append(ProjectMemberType(
            user=UserType(
                id=str(access.user.public_id),
                email=access.user.email,
                username=access.user.username,
                is_active=access.user.is_active,
                is_superuser=access.user.is_superuser,
                onboarding_completed=access.user.onboarding_completed
            ),
            role=access.role,
            created_at=access.created_at
        ))
    
    # Check if current user can edit
    can_edit = project.owner_id == current_user_id
    if not can_edit:
        for access in project.access_members:
            if access.user_id == current_user_id and access.role == "admin":
                can_edit = True
                break
    
    # Build languages configuration
    languages = []
    if project.languages:
        for lang in project.languages:
            # lang is always a dict with 'code', 'locale', and 'direction'
            code = lang.get('code', '')
            languages.append(LanguageConfigType(
                code=code,
                locale=lang.get('locale', ''),
                direction=lang.get('direction', LANGUAGE_CONFIGS.get(code, {}).get('direction', 'ltr')),
                plural_forms=get_plural_forms(code),
                default=code == project.default_language
            ))
    
    # Calculate translation progress using SQL stats (much faster!)
    keys_count = stats.get('keys_count', 0) if stats else 0
    translations_count = stats.get('translations_count', 0) if stats else 0
    languages_count = len(project.languages) if project.languages else 0
    
    if keys_count == 0 or languages_count == 0:
        translation_progress = 0
    else:
        total_required = keys_count * languages_count
        # translations_count already includes only non-empty translations from SQL
        translation_progress = int((translations_count / total_required) * 100) if total_required > 0 else 0
    
    # Get language-specific progress if database session is provided
    language_progress = []
    if db:
        from app.services.project_service import ProjectService
        lang_progress_data = await ProjectService.get_language_progress(db, project.id)
        
        # Build language progress list, ensuring all configured languages are included
        for lang in project.languages:
            lang_code = lang.get('code', '')
            if lang_code in lang_progress_data:
                language_progress.append(LanguageProgressType(
                    code=lang_code,
                    progress=lang_progress_data[lang_code]['progress'],
                    completed=lang_progress_data[lang_code]['completed'],
                    total=lang_progress_data[lang_code]['total']
                ))
            else:
                # Language has no translations yet
                language_progress.append(LanguageProgressType(
                    code=lang_code,
                    progress=0,
                    completed=0,
                    total=keys_count
                ))
    
    return ProjectType(
        id=str(project.public_id),
        name=project.name,
        description=project.description,
        languages=languages,
        default_language=project.default_language,
        available_tags=project.available_tags or [],
        color=project.color,
        status=project.status,
        team=team,
        owner=owner,
        access_members=access_members,
        can_edit=can_edit,
        keys_count=keys_count,
        translation_progress=translation_progress,
        language_progress=language_progress,
        created_at=project.created_at,
        updated_at=project.updated_at
    )


@strawberry.type
class ProjectQuery:
    """
    GraphQL queries for projects.
    """

    @strawberry.field
    def available_languages(self) -> List[AvailableLanguageType]:
        """
        Get all available languages with their full configurations.
        This is the single source of truth for language metadata.
        
        Returns:
            List of all supported languages with metadata
        """
        languages = get_all_languages()
        return [
            AvailableLanguageType(
                code=lang['code'],
                name=lang['name'],
                native_name=lang['native_name'],
                flag=lang['flag'],
                locale=lang['locale'],
                direction=lang['direction'],
                plural_forms=lang['plural_forms'],
                detection_patterns=DetectionPatternsType(
                    end_patterns=lang['detection_patterns']['end_patterns'],
                    middle_patterns=lang['detection_patterns']['middle_patterns'],
                    start_patterns=lang['detection_patterns']['start_patterns'],
                    full_names=lang['detection_patterns']['full_names'],
                )
            )
            for lang in languages
        ]

    @strawberry.field
    async def projects(self, info: Info) -> List[ProjectType]:
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
            current_user_id = await get_current_user_id(info)
            if not current_user_id:
                raise UnauthorizedError("Authentication required to access projects")
            
            async with AsyncSessionLocal() as db:
                projects = await ProjectService.get_user_projects(db, current_user_id)
                
                # Get statistics for all projects in one SQL query
                project_ids = [p.id for p in projects]
                stats = await ProjectService.get_projects_stats(db, project_ids) if project_ids else {}
                
                # Build project types and filter out None values (projects with missing relations)
                result = []
                for project in projects:
                    project_type = await build_project_type(project, current_user_id, stats.get(project.id), db)
                    if project_type:
                        result.append(project_type)
                return result
        except UnauthorizedError:
            # Re-raise authentication errors
            raise
        except Exception as e:
            logger.error(f"Error in projects query: {type(e).__name__}: {str(e)}")
            return []

    @strawberry.field
    async def project(self, info: Info, id: str) -> Optional[ProjectType]:
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
            current_user_id = await get_current_user_id(info)
            if not current_user_id:
                return None
            
            async with AsyncSessionLocal() as db:
                project = await ProjectService.get_project_by_public_id(db, id)
                if not project:
                    return None
                
                # Check access
                if not await ProjectService.check_project_access(db, project.id, current_user_id):
                    return None
                
                # Get statistics for this project
                stats = await ProjectService.get_projects_stats(db, [project.id])
                
                return await build_project_type(project, current_user_id, stats.get(project.id), db)
        except Exception as e:
            logger.error(f"Error in project query: {type(e).__name__}: {str(e)}")
            return None


@strawberry.type
class ProjectMutation:
    """
    GraphQL mutations for projects.
    """

    @strawberry.mutation
    async def create_project(self, input: CreateProjectInput, info: Info) -> ProjectType:
        """
        Create a new project in a team.
        
        Args:
            input: Project creation input
            info: GraphQL info object
            
        Returns:
            Created project
            
        Raises:
            UnauthorizedError: If user is not authenticated
            DatabaseError: If database operation fails
        """
        from app.services.team_service import TeamService
        
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to create projects")
        
        async with AsyncSessionLocal() as db:
            try:
                # Get team by public_id
                team = await TeamService.get_team_by_public_id(db, input.team_id)
                if not team:
                    raise UnauthorizedError("Team not found")
                
                # Verify user has access to team
                if not await TeamService.check_user_team_access(db, team.id, current_user_id):
                    raise UnauthorizedError("User does not have access to this team")
                
                project = await ProjectService.create_project(
                    db=db,
                    owner_id=current_user_id,
                    team_id=team.id,
                    name=input.name,
                    description=input.description,
                    languages=input.languages or [],
                    default_language=input.default_language,
                    color=input.color or "#6366f1",
                    status=input.status or "active"
                )
                
                # New project has no keys/translations yet
                stats = {'keys_count': 0, 'translations_count': 0}
                return await build_project_type(project, current_user_id, stats, db)
            except (UnauthorizedError, AuthenticationError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "project creation")
            except Exception as e:
                handle_database_exception(e, "project creation")

    @strawberry.mutation
    async def update_project(self, input: UpdateProjectInput, info: Info) -> Optional[ProjectType]:
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
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to update projects")
        
        async with AsyncSessionLocal() as db:
            try:
                project = await ProjectService.update_project(
                    db=db,
                    public_id=input.id,
                    user_id=current_user_id,
                    name=input.name,
                    description=input.description,
                    languages=input.languages,
                    default_language=input.default_language,
                    color=input.color,
                    status=input.status
                )
                
                if not project:
                    return None
                
                # Get statistics for the updated project
                stats = await ProjectService.get_projects_stats(db, [project.id])
                return await build_project_type(project, current_user_id, stats.get(project.id), db)
            except (UnauthorizedError, AuthenticationError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "project update")
            except Exception as e:
                handle_database_exception(e, "project update")

    @strawberry.mutation
    async def delete_project(self, id: str, info: Info) -> bool:
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
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to delete projects")
        
        async with AsyncSessionLocal() as db:
            try:
                return await ProjectService.delete_project(db, id, current_user_id)
            except (UnauthorizedError, AuthenticationError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "project deletion")
            except Exception as e:
                handle_database_exception(e, "project deletion")

    @strawberry.mutation
    async def add_project_member(self, input: AddProjectMemberInput, info: Info) -> Optional[ProjectType]:
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
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to add project members")
        
        async with AsyncSessionLocal() as db:
            try:
                member = await ProjectService.add_project_member(
                    db=db,
                    project_public_id=input.project_id,
                    user_public_id=input.user_id,
                    role=input.role,
                    added_by_user_id=current_user_id
                )
                
                if not member:
                    return None
                
                # Get updated project with eager loading
                from app.models.project import Project as ProjectModel, ProjectMember
                from sqlalchemy.orm import joinedload, selectinload
                
                result = await db.execute(
                    select(ProjectModel)
                    .options(
                        joinedload(ProjectModel.owner),
                        selectinload(ProjectModel.members).joinedload(ProjectMember.user)
                    )
                    .where(ProjectModel.id == member.project_id)
                )
                project = result.scalar_one_or_none()
                
                if not project:
                    return None
                
                # Get statistics for the project
                stats = await ProjectService.get_projects_stats(db, [project.id])
                return await build_project_type(project, current_user_id, stats.get(project.id), db)
            except (UnauthorizedError, AuthenticationError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "adding project member")
            except Exception as e:
                handle_database_exception(e, "adding project member")

