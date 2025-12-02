import strawberry
from typing import Optional, List
from datetime import datetime
from strawberry.types import Info
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError, OperationalError
import logging
import enum

from app.database import AsyncSessionLocal
from app.services.key_service import KeyService
from app.core.exceptions import (
    AuthenticationError,
    UnauthorizedError,
    handle_database_exception
)
from app.schemas.project import get_current_user_id
from app.schemas.auth import UserType

logger = logging.getLogger(__name__)


class ActionTypeEnum(str, enum.Enum):
    """
    GraphQL enum for all activity log action types.
    """
    # Team lifecycle
    TEAM_CREATE = "TEAM_CREATE"
    TEAM_UPDATE_NAME = "TEAM_UPDATE_NAME"
    TEAM_UPDATE_DESCRIPTION = "TEAM_UPDATE_DESCRIPTION"
    TEAM_DELETE = "TEAM_DELETE"
    
    # Project actions
    PROJECT_CREATE = "PROJECT_CREATE"
    PROJECT_UPDATE_NAME = "PROJECT_UPDATE_NAME"
    PROJECT_UPDATE_DESCRIPTION = "PROJECT_UPDATE_DESCRIPTION"
    PROJECT_UPDATE_LANGUAGES = "PROJECT_UPDATE_LANGUAGES"
    PROJECT_UPDATE_DEFAULT_LANGUAGE = "PROJECT_UPDATE_DEFAULT_LANGUAGE"
    PROJECT_UPDATE_COLOR = "PROJECT_UPDATE_COLOR"
    PROJECT_UPDATE_STATUS = "PROJECT_UPDATE_STATUS"
    PROJECT_DELETE = "PROJECT_DELETE"
    PROJECT_EXPORT = "PROJECT_EXPORT"
    PROJECT_IMPORT = "PROJECT_IMPORT"
    
    # Team management
    MEMBER_ADD = "MEMBER_ADD"
    MEMBER_REMOVE = "MEMBER_REMOVE"
    MEMBER_ROLE_CHANGE = "MEMBER_ROLE_CHANGE"
    TEAM_INVITE = "TEAM_INVITE"
    
    # Key actions
    KEY_CREATE = "KEY_CREATE"
    KEY_UPDATE = "KEY_UPDATE"
    KEY_UPDATE_DESCRIPTION = "KEY_UPDATE_DESCRIPTION"
    KEY_DELETE = "KEY_DELETE"
    
    # Translation actions
    TRANSLATION_UPDATE = "TRANSLATION_UPDATE"
    TRANSLATION_AI_UPDATE = "TRANSLATION_AI_UPDATE"
    TRANSLATION_DELETE = "TRANSLATION_DELETE"
    TRANSLATION_IMPORT = "TRANSLATION_IMPORT"
    
    # Batch import action
    KEYS_BATCH_IMPORT = "KEYS_BATCH_IMPORT"
    
    # Review actions
    REVIEW_APPROVE = "REVIEW_APPROVE"
    REVIEW_REJECT = "REVIEW_REJECT"
    REVIEW_DELETE = "REVIEW_DELETE"


# Keep legacy enum for backward compatibility (optional)
KeyActionTypeEnum = ActionTypeEnum


class ReviewStatusEnum(str, enum.Enum):
    """
    GraphQL enum for review status.
    """
    NOT_REVIEWED = "NOT_REVIEWED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# Register as Strawberry enums
ActionTypeEnum = strawberry.enum(ActionTypeEnum)
ReviewStatusEnum = strawberry.enum(ReviewStatusEnum)


@strawberry.type
class ActivityProjectInfo:
    """
    Simplified project info for activity logs (to avoid circular dependency).
    """
    id: str
    name: str
    color: Optional[str]


@strawberry.type
class ActivityLogType:
    """
    GraphQL type for Activity Log (universal audit trail).
    """
    id: int
    project_id: Optional[int]
    key_id: Optional[int]
    user_id: Optional[int]
    affected_user_id: Optional[int]
    user: Optional['UserType']
    affected_user: Optional['UserType']
    project: Optional[ActivityProjectInfo]
    action: ActionTypeEnum
    field_name: Optional[str]
    language: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    extra_data: Optional[strawberry.scalars.JSON] = None
    created_at: datetime


# Keep legacy type for backward compatibility
KeyLogType = ActivityLogType


@strawberry.type
class TranslationType:
    """
    GraphQL type for Translation.
    """
    language: str
    value: str
    review_status: ReviewStatusEnum
    created_at: datetime
    updated_at: Optional[datetime]


@strawberry.type
class KeyType:
    """
    GraphQL type for Key.
    """
    id: str  # UUID as string for public API
    key: str
    description: Optional[str]
    tags: List[str]
    is_plural: bool
    translations: List[TranslationType]
    created_at: datetime
    updated_at: Optional[datetime]


@strawberry.type
class KeysConnection:
    """
    Paginated response type for keys.
    """
    keys: List[KeyType]
    total_count: int
    has_more: bool


@strawberry.type
class BatchImportResult:
    """
    Result type for batch import operation.
    """
    success_count: int
    error_count: int
    created_keys: int
    updated_keys: int
    errors: List[str]


@strawberry.input
class CreateKeyInput:
    """
    Input type for creating a key.
    """
    project_id: str  # Project UUID
    key: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_plural: Optional[bool] = False  # Whether this key uses plural forms
    translations: Optional[strawberry.scalars.JSON] = None  # Dict[str, str]
    autopilot: Optional[bool] = False  # Auto-translate to all languages using AI


@strawberry.input
class UpdateKeyInput:
    """
    Input type for updating a key.
    """
    id: str  # Key UUID
    key: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_plural: Optional[bool] = None  # Whether this key uses plural forms


@strawberry.input
class SetTranslationInput:
    """
    Input type for setting a translation.
    """
    key_id: str  # Key UUID
    language: str
    value: str
    is_ai_generated: Optional[bool] = False


@strawberry.input
class DeleteTranslationInput:
    """
    Input type for deleting a translation.
    """
    key_id: str  # Key UUID
    language: str


@strawberry.input
class BatchTranslationInput:
    """
    Input type for batch translation import.
    """
    key: str
    value: str


@strawberry.input
class BatchImportInput:
    """
    Input type for batch importing translations.
    """
    project_id: str  # Project UUID
    language: str
    translations: List[BatchTranslationInput]
    strategy: str = "merge"  # 'merge' or 'replace'


@strawberry.input
class ApproveTranslationInput:
    """
    Input type for approving a translation.
    """
    key_id: str  # Key UUID
    language: str  # Language code
    comment: Optional[str] = None


@strawberry.input
class RejectTranslationInput:
    """
    Input type for rejecting a translation.
    """
    key_id: str  # Key UUID
    language: str  # Language code
    comment: Optional[str] = None


def build_key_type(key) -> KeyType:
    """
    Build KeyType from Key model.
    
    Args:
        key: Key model instance
        
    Returns:
        KeyType
    """
    # Build translations
    translations = []
    for translation in key.translations:
        translations.append(TranslationType(
            language=translation.language,
            value=translation.value,
            review_status=ReviewStatusEnum(translation.review_status.value),
            created_at=translation.created_at,
            updated_at=translation.updated_at
        ))
    
    return KeyType(
        id=str(key.public_id),
        key=key.key,
        description=key.description,
        tags=key.tags or [],
        is_plural=key.is_plural or False,
        translations=translations,
        created_at=key.created_at,
        updated_at=key.updated_at
    )


def build_activity_log_type(log) -> ActivityLogType:
    """
    Build ActivityLogType from ActivityLog model.
    
    Args:
        log: ActivityLog model instance
        
    Returns:
        ActivityLogType
    """
    # Map action to enum
    action_map = {
        # Team lifecycle
        "TEAM_CREATE": ActionTypeEnum.TEAM_CREATE,
        "TEAM_UPDATE_NAME": ActionTypeEnum.TEAM_UPDATE_NAME,
        "TEAM_UPDATE_DESCRIPTION": ActionTypeEnum.TEAM_UPDATE_DESCRIPTION,
        "TEAM_DELETE": ActionTypeEnum.TEAM_DELETE,
        
        # Project actions
        "PROJECT_CREATE": ActionTypeEnum.PROJECT_CREATE,
        "PROJECT_UPDATE_NAME": ActionTypeEnum.PROJECT_UPDATE_NAME,
        "PROJECT_UPDATE_DESCRIPTION": ActionTypeEnum.PROJECT_UPDATE_DESCRIPTION,
        "PROJECT_UPDATE_LANGUAGES": ActionTypeEnum.PROJECT_UPDATE_LANGUAGES,
        "PROJECT_UPDATE_DEFAULT_LANGUAGE": ActionTypeEnum.PROJECT_UPDATE_DEFAULT_LANGUAGE,
        "PROJECT_UPDATE_COLOR": ActionTypeEnum.PROJECT_UPDATE_COLOR,
        "PROJECT_UPDATE_STATUS": ActionTypeEnum.PROJECT_UPDATE_STATUS,
        "PROJECT_DELETE": ActionTypeEnum.PROJECT_DELETE,
        "PROJECT_EXPORT": ActionTypeEnum.PROJECT_EXPORT,
        "PROJECT_IMPORT": ActionTypeEnum.PROJECT_IMPORT,
        
        # Team management
        "MEMBER_ADD": ActionTypeEnum.MEMBER_ADD,
        "MEMBER_REMOVE": ActionTypeEnum.MEMBER_REMOVE,
        "MEMBER_ROLE_CHANGE": ActionTypeEnum.MEMBER_ROLE_CHANGE,
        "TEAM_INVITE": ActionTypeEnum.TEAM_INVITE,
        
        # Key actions
        "KEY_CREATE": ActionTypeEnum.KEY_CREATE,
        "KEY_UPDATE": ActionTypeEnum.KEY_UPDATE,
        "KEY_UPDATE_DESCRIPTION": ActionTypeEnum.KEY_UPDATE_DESCRIPTION,
        "KEY_DELETE": ActionTypeEnum.KEY_DELETE,
        
        # Translation actions
        "TRANSLATION_UPDATE": ActionTypeEnum.TRANSLATION_UPDATE,
        "TRANSLATION_AI_UPDATE": ActionTypeEnum.TRANSLATION_AI_UPDATE,
        "TRANSLATION_DELETE": ActionTypeEnum.TRANSLATION_DELETE,
        "TRANSLATION_IMPORT": ActionTypeEnum.TRANSLATION_IMPORT,
        
        # Batch import action
        "KEYS_BATCH_IMPORT": ActionTypeEnum.KEYS_BATCH_IMPORT,
        
        # Review actions
        "REVIEW_APPROVE": ActionTypeEnum.REVIEW_APPROVE,
        "REVIEW_REJECT": ActionTypeEnum.REVIEW_REJECT,
        "REVIEW_DELETE": ActionTypeEnum.REVIEW_DELETE,
    }
    
    # Build user info if available
    user = None
    if log.user:
        user = UserType(
            id=str(log.user.public_id),
            email=log.user.email,
            username=log.user.username,
            is_active=log.user.is_active,
            is_superuser=log.user.is_superuser,
            onboarding_completed=log.user.onboarding_completed
        )
    
    # Build affected user info if available
    affected_user = None
    if log.affected_user:
        affected_user = UserType(
            id=str(log.affected_user.public_id),
            email=log.affected_user.email,
            username=log.affected_user.username,
            is_active=log.affected_user.is_active,
            is_superuser=log.affected_user.is_superuser,
            onboarding_completed=log.affected_user.onboarding_completed
        )
    
    # Build project info if available
    project = None
    if log.project:
        project = ActivityProjectInfo(
            id=str(log.project.public_id),
            name=log.project.name,
            color=log.project.color
        )
    
    return ActivityLogType(
        id=log.id,
        project_id=log.project_id,
        key_id=log.key_id,
        user_id=log.user_id,
        affected_user_id=log.affected_user_id,
        user=user,
        affected_user=affected_user,
        project=project,
        action=action_map.get(log.action.value, ActionTypeEnum.KEY_UPDATE),
        field_name=log.field_name,
        language=log.language,
        old_value=log.old_value,
        new_value=log.new_value,
        extra_data=log.extra_data,
        created_at=log.created_at
    )


# Legacy function for backward compatibility
build_key_log_type = build_activity_log_type


@strawberry.type
class KeyQuery:
    """
    GraphQL queries for keys.
    """

    @strawberry.field
    async def project_keys(
        self, 
        info: Info, 
        project_id: str,
        offset: Optional[int] = 0,
        limit: Optional[int] = 50,
        search: Optional[str] = None
    ) -> KeysConnection:
        """
        Get keys for a project with pagination and search support.
        
        Args:
            info: GraphQL info object
            project_id: Project UUID
            offset: Number of keys to skip (default: 0)
            limit: Maximum number of keys to return (default: 50)
            search: Optional search query to filter keys (default: None)
            
        Returns:
            Paginated keys with total count
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        try:
            current_user_id = await get_current_user_id(info)
            if not current_user_id:
                raise UnauthorizedError("Authentication required to access keys")
            
            # Validate pagination parameters
            if offset is None or offset < 0:
                offset = 0
            if limit is None or limit <= 0:
                limit = 50
            # Cap maximum limit to prevent abuse
            if limit > 200:
                limit = 200
            
            async with AsyncSessionLocal() as db:
                result = await KeyService.get_project_keys_paginated(
                    db, 
                    project_id, 
                    current_user_id,
                    offset=offset,
                    limit=limit,
                    search=search
                )
                
                if result is None:
                    return KeysConnection(keys=[], total_count=0, has_more=False)
                
                keys = [build_key_type(key) for key in result['keys']]
                total_count = result['total_count']
                has_more = (offset + limit) < total_count
                
                return KeysConnection(
                    keys=keys,
                    total_count=total_count,
                    has_more=has_more
                )
        except UnauthorizedError:
            raise
        except Exception as e:
            # Log technical error details with full traceback
            logger.error(f"Error in project_keys query: {type(e).__name__}: {str(e)}", exc_info=True)
            # Raise user-friendly error that doesn't expose internals
            from app.core.exceptions import DatabaseError
            raise DatabaseError(internal_message=f"Error loading keys: {type(e).__name__}: {str(e)}")

    @strawberry.field
    async def key(self, info: Info, id: str) -> Optional[KeyType]:
        """
        Get a specific key by ID.
        
        Args:
            info: GraphQL info object
            id: Key UUID
            
        Returns:
            Key or None
        """
        try:
            current_user_id = await get_current_user_id(info)
            if not current_user_id:
                return None
            
            async with AsyncSessionLocal() as db:
                key = await KeyService.get_key_by_public_id(db, id)
                if not key:
                    return None
                
                # Check access through project
                from app.services.project_service import ProjectService
                if not await ProjectService.check_project_access(db, key.project_id, current_user_id):
                    return None
                
                return build_key_type(key)
        except Exception as e:
            logger.error(f"Error in key query: {type(e).__name__}: {str(e)}")
            return None

    @strawberry.field
    async def check_key_exists(self, info: Info, project_id: str, key: str) -> bool:
        """
        Check if a key already exists in a project.
        
        Args:
            info: GraphQL info object
            project_id: Project UUID
            key: Key string to check
            
        Returns:
            True if key exists, False otherwise
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        try:
            current_user_id = await get_current_user_id(info)
            if not current_user_id:
                raise UnauthorizedError("Authentication required to check keys")
            
            async with AsyncSessionLocal() as db:
                exists = await KeyService.check_key_exists(db, project_id, key, current_user_id)
                if exists is None:
                    return False
                
                return exists
        except UnauthorizedError:
            raise
        except Exception as e:
            logger.error(f"Error in check_key_exists query: {type(e).__name__}: {str(e)}")
            return False

    @strawberry.field
    async def key_logs(self, info: Info, key_id: str, limit: Optional[int] = 50) -> List[KeyLogType]:
        """
        Get audit logs for a specific key.
        
        Args:
            info: GraphQL info object
            key_id: Key UUID
            limit: Maximum number of logs to return (default: 50)
            
        Returns:
            List of key logs ordered by created_at DESC
            
        Raises:
            UnauthorizedError: If user is not authenticated or doesn't have access
        """
        try:
            current_user_id = await get_current_user_id(info)
            if not current_user_id:
                raise UnauthorizedError("Authentication required to view logs")
            
            async with AsyncSessionLocal() as db:
                # Get key to check access
                key = await KeyService.get_key_by_public_id(db, key_id, eager_load_translations=False)
                if not key:
                    return []
                
                # Check access through project
                from app.services.project_service import ProjectService
                if not await ProjectService.check_project_access(db, key.project_id, current_user_id):
                    raise UnauthorizedError("You don't have access to this key")
                
                # Get logs with eager loading of user and project
                from app.models.activity_log import ActivityLog
                from app.models.project import Project as ProjectModel
                result = await db.execute(
                    select(ActivityLog)
                    .options(
                        joinedload(ActivityLog.user),
                        joinedload(ActivityLog.affected_user),
                        joinedload(ActivityLog.project)
                    )
                    .where(ActivityLog.key_id == key.id)
                    .order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc())
                    .limit(limit or 50)
                )
                logs = result.scalars().unique().all()
                
                return [build_activity_log_type(log) for log in logs]
        except UnauthorizedError:
            raise
        except Exception as e:
            logger.error(f"Error in key_logs query: {type(e).__name__}: {str(e)}")
            return []

    @strawberry.field
    async def project_activity(self, info: Info, project_id: str, limit: Optional[int] = 100) -> List[ActivityLogType]:
        """
        Get all activity logs for a project (including key and translation changes).
        
        Args:
            info: GraphQL info object
            project_id: Project UUID
            limit: Maximum number of logs to return (default: 100)
            
        Returns:
            List of activity logs ordered by created_at DESC
            
        Raises:
            UnauthorizedError: If user is not authenticated or doesn't have access
        """
        try:
            current_user_id = await get_current_user_id(info)
            if not current_user_id:
                raise UnauthorizedError("Authentication required to view activity")
            
            async with AsyncSessionLocal() as db:
                # Get project to check access
                from app.services.project_service import ProjectService
                project = await ProjectService.get_project_by_public_id(db, project_id)
                if not project:
                    return []
                
                # Check access
                if not await ProjectService.check_project_access(db, project.id, current_user_id):
                    raise UnauthorizedError("You don't have access to this project")
                
                # Get all logs for this project with eager loading
                from app.models.activity_log import ActivityLog
                result = await db.execute(
                    select(ActivityLog)
                    .options(
                        joinedload(ActivityLog.user),
                        joinedload(ActivityLog.affected_user)
                    )
                    .where(ActivityLog.project_id == project.id)
                    .order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc())
                    .limit(limit or 100)
                )
                logs = result.scalars().all()
                
                return [build_activity_log_type(log) for log in logs]
        except UnauthorizedError:
            raise
        except Exception as e:
            logger.error(f"Error in project_activity query: {type(e).__name__}: {str(e)}")
            return []


@strawberry.type
class KeyMutation:
    """
    GraphQL mutations for keys.
    """

    @strawberry.mutation
    async def create_key(self, input: CreateKeyInput, info: Info) -> Optional[KeyType]:
        """
        Create a new key with optional AI autopilot translation.
        
        Args:
            input: Key creation input
            info: GraphQL info object
            
        Returns:
            Created key
            
        Raises:
            UnauthorizedError: If user is not authenticated
            DatabaseError: If database operation fails
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to create keys")
        
        async with AsyncSessionLocal() as db:
            try:
                # Create the key first
                key = await KeyService.create_key(
                    db=db,
                    project_public_id=input.project_id,
                    key=input.key,
                    description=input.description,
                    tags=input.tags,
                    is_plural=input.is_plural or False,
                    translations=input.translations,
                    user_id=current_user_id
                )
                
                if not key:
                    return None
                
                # Run autopilot translation if enabled and default translation provided
                autopilot_enabled = input.autopilot if input.autopilot is not None else False
                
                if autopilot_enabled and input.translations:
                    # Get project for autopilot
                    from app.services.project_service import ProjectService
                    project = await ProjectService.get_project_by_public_id(db, input.project_id)
                    
                    if project and project.default_language:
                        default_lang = project.default_language
                        default_value = input.translations.get(default_lang)
                        
                        if default_value:
                            # Run autopilot translation
                            success, errors, error_msgs = await KeyService.autopilot_translate(
                                db=db,
                                key=key,
                                source_text=default_value,
                                source_language=default_lang,
                                project=project,
                                user_id=current_user_id,
                                context=input.description
                            )
                            
                            if errors > 0:
                                logger.warning(
                                    f"Autopilot translation had {errors} errors for key {key.key}: "
                                    f"{error_msgs}"
                                )
                            
                            # Reload key with translations after autopilot
                            from sqlalchemy import select
                            from sqlalchemy.orm import joinedload
                            from app.models.key import Key as KeyModel
                            result = await db.execute(
                                select(KeyModel)
                                .options(joinedload(KeyModel.translations))
                                .where(KeyModel.id == key.id)
                                .execution_options(populate_existing=True)
                            )
                            key = result.unique().scalar_one()
                
                return build_key_type(key)
            except (UnauthorizedError, AuthenticationError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "key creation")
            except Exception as e:
                handle_database_exception(e, "key creation")

    @strawberry.mutation
    async def update_key(self, input: UpdateKeyInput, info: Info) -> Optional[KeyType]:
        """
        Update an existing key.
        
        Args:
            input: Key update input
            info: GraphQL info object
            
        Returns:
            Updated key or None
            
        Raises:
            UnauthorizedError: If user is not authenticated
            DatabaseError: If database operation fails
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to update keys")
        
        async with AsyncSessionLocal() as db:
            try:
                key = await KeyService.update_key(
                    db=db,
                    public_id=input.id,
                    key=input.key,
                    description=input.description,
                    tags=input.tags,
                    is_plural=input.is_plural,
                    user_id=current_user_id
                )
                
                if not key:
                    return None
                
                return build_key_type(key)
            except (UnauthorizedError, AuthenticationError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "key update")
            except Exception as e:
                handle_database_exception(e, "key update")

    @strawberry.mutation
    async def delete_key(self, id: str, info: Info) -> bool:
        """
        Delete a key.
        
        Args:
            id: Key UUID
            info: GraphQL info object
            
        Returns:
            True if deleted, False otherwise
            
        Raises:
            UnauthorizedError: If user is not authenticated
            DatabaseError: If database operation fails
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to delete keys")
        
        async with AsyncSessionLocal() as db:
            try:
                return await KeyService.delete_key(db, id, current_user_id)
            except (UnauthorizedError, AuthenticationError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "key deletion")
            except Exception as e:
                handle_database_exception(e, "key deletion")

    @strawberry.mutation
    async def set_translation(self, input: SetTranslationInput, info: Info) -> Optional[TranslationType]:
        """
        Set or update a translation.
        
        Args:
            input: Translation input
            info: GraphQL info object
            
        Returns:
            Created/updated translation or None
            
        Raises:
            UnauthorizedError: If user is not authenticated
            DatabaseError: If database operation fails
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to set translations")
        
        async with AsyncSessionLocal() as db:
            try:
                translation = await KeyService.set_translation(
                    db=db,
                    key_public_id=input.key_id,
                    language=input.language,
                    value=input.value,
                    user_id=current_user_id,
                    is_ai_generated=input.is_ai_generated or False
                )
                
                if not translation:
                    return None
                
                return TranslationType(
                    language=translation.language,
                    value=translation.value,
                    review_status=ReviewStatusEnum(translation.review_status.value),
                    created_at=translation.created_at,
                    updated_at=translation.updated_at
                )
            except (UnauthorizedError, AuthenticationError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "translation update")
            except Exception as e:
                handle_database_exception(e, "translation update")

    @strawberry.mutation
    async def delete_translation(self, input: DeleteTranslationInput, info: Info) -> bool:
        """
        Delete a translation.
        
        Args:
            input: Delete translation input
            info: GraphQL info object
            
        Returns:
            True if deleted, False otherwise
            
        Raises:
            UnauthorizedError: If user is not authenticated
            DatabaseError: If database operation fails
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to delete translations")
        
        async with AsyncSessionLocal() as db:
            try:
                return await KeyService.delete_translation(
                    db=db,
                    key_public_id=input.key_id,
                    language=input.language,
                    user_id=current_user_id
                )
            except (UnauthorizedError, AuthenticationError):
                raise
            except (IntegrityError, OperationalError) as e:
                handle_database_exception(e, "translation deletion")
            except Exception as e:
                handle_database_exception(e, "translation deletion")

    @strawberry.mutation
    async def batch_import_translations(self, input: BatchImportInput, info: Info) -> BatchImportResult:
        """
        Batch import translations for a specific language.
        
        Args:
            input: Batch import input with translations
            info: GraphQL info object
            
        Returns:
            Result with success/error counts
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to import translations")
        
        async with AsyncSessionLocal() as db:
            try:
                result = await KeyService.batch_import_translations(
                    db=db,
                    project_public_id=input.project_id,
                    language=input.language,
                    translations=input.translations,
                    strategy=input.strategy,
                    user_id=current_user_id
                )
                
                return BatchImportResult(
                    success_count=result['success_count'],
                    error_count=result['error_count'],
                    created_keys=result['created_keys'],
                    updated_keys=result['updated_keys'],
                    errors=result['errors']
                )
            except (UnauthorizedError, AuthenticationError):
                raise
            except Exception as e:
                logger.error(f"Error in batch import: {type(e).__name__}: {str(e)}")
                return BatchImportResult(
                    success_count=0,
                    error_count=len(input.translations),
                    created_keys=0,
                    updated_keys=0,
                    errors=[str(e)]
                )

    @strawberry.mutation
    async def approve_translation(self, input: ApproveTranslationInput, info: Info) -> Optional[KeyType]:
        """
        Approve a translation.
        
        Args:
            input: Approve translation input
            info: GraphQL info object
            
        Returns:
            Updated key or None
            
        Raises:
            UnauthorizedError: If user is not authenticated
            DatabaseError: If database operation fails
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to approve translations")
        
        async with AsyncSessionLocal() as db:
            try:
                key = await KeyService.approve_translation(
                    db=db,
                    key_public_id=input.key_id,
                    language=input.language,
                    user_id=current_user_id,
                    comment=input.comment
                )
                
                if not key:
                    return None
                
                return build_key_type(key)
            except (UnauthorizedError, AuthenticationError):
                raise
            except Exception as e:
                handle_database_exception(e, "translation approval")

    @strawberry.mutation
    async def reject_translation(self, input: RejectTranslationInput, info: Info) -> Optional[KeyType]:
        """
        Reject a translation.
        
        Args:
            input: Reject translation input
            info: GraphQL info object
            
        Returns:
            Updated key or None
            
        Raises:
            UnauthorizedError: If user is not authenticated
            DatabaseError: If database operation fails
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to reject translations")
        
        async with AsyncSessionLocal() as db:
            try:
                key = await KeyService.reject_translation(
                    db=db,
                    key_public_id=input.key_id,
                    language=input.language,
                    user_id=current_user_id,
                    comment=input.comment
                )
                
                if not key:
                    return None
                
                return build_key_type(key)
            except (UnauthorizedError, AuthenticationError):
                raise
            except Exception as e:
                handle_database_exception(e, "translation rejection")

    @strawberry.mutation
    async def delete_translation_review(self, key_id: str, language: str, info: Info) -> Optional[KeyType]:
        """
        Delete review status and reset translation to pending.
        
        Args:
            key_id: Key UUID
            language: Language code
            info: GraphQL info object
            
        Returns:
            Updated key or None
            
        Raises:
            UnauthorizedError: If user is not authenticated
            DatabaseError: If database operation fails
        """
        current_user_id = await get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to delete reviews")
        
        async with AsyncSessionLocal() as db:
            try:
                key = await KeyService.delete_translation_review(
                    db=db,
                    key_public_id=key_id,
                    language=language,
                    user_id=current_user_id
                )
                
                if not key:
                    return None
                
                return build_key_type(key)
            except (UnauthorizedError, AuthenticationError):
                raise
            except Exception as e:
                handle_database_exception(e, "review deletion")

