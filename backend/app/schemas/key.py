import strawberry
from typing import Optional, List
from datetime import datetime
from strawberry.types import Info
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, OperationalError
import logging
import enum

from app.database import get_db
from app.services.key_service import KeyService
from app.core.exceptions import (
    AuthenticationError,
    UnauthorizedError,
    handle_database_exception
)
from app.schemas.project import get_current_user_id
from app.schemas.auth import UserType

logger = logging.getLogger(__name__)


class KeyActionTypeEnum(str, enum.Enum):
    """
    GraphQL enum for key action types.
    """
    CREATE = "create"
    UPDATE_KEY = "update_key"
    UPDATE_DESCRIPTION = "update_description"
    UPDATE_TRANSLATION = "update_translation"
    DELETE_TRANSLATION = "delete_translation"
    DELETE = "delete"


# Register as Strawberry enum
KeyActionTypeEnum = strawberry.enum(KeyActionTypeEnum)


@strawberry.type
class KeyLogType:
    """
    GraphQL type for Key Log (audit trail).
    """
    id: int
    key_id: int
    user_id: Optional[int]
    user: Optional['UserType']
    action: KeyActionTypeEnum
    field_name: Optional[str]
    language: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    created_at: datetime


@strawberry.type
class TranslationType:
    """
    GraphQL type for Translation.
    """
    language: str
    value: str
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
    translations: List[TranslationType]
    created_at: datetime
    updated_at: Optional[datetime]


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
    translations: Optional[strawberry.scalars.JSON] = None  # Dict[str, str]


@strawberry.input
class UpdateKeyInput:
    """
    Input type for updating a key.
    """
    id: str  # Key UUID
    key: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


@strawberry.input
class SetTranslationInput:
    """
    Input type for setting a translation.
    """
    key_id: str  # Key UUID
    language: str
    value: str


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
            created_at=translation.created_at,
            updated_at=translation.updated_at
        ))
    
    return KeyType(
        id=str(key.public_id),
        key=key.key,
        description=key.description,
        tags=key.tags or [],
        translations=translations,
        created_at=key.created_at,
        updated_at=key.updated_at
    )


def build_key_log_type(log) -> KeyLogType:
    """
    Build KeyLogType from KeyLog model.
    
    Args:
        log: KeyLog model instance
        
    Returns:
        KeyLogType
    """
    # Map action to enum
    action_map = {
        "create": KeyActionTypeEnum.CREATE,
        "update_key": KeyActionTypeEnum.UPDATE_KEY,
        "update_description": KeyActionTypeEnum.UPDATE_DESCRIPTION,
        "update_translation": KeyActionTypeEnum.UPDATE_TRANSLATION,
        "delete_translation": KeyActionTypeEnum.DELETE_TRANSLATION,
        "delete": KeyActionTypeEnum.DELETE,
    }
    
    # Build user info if available
    user = None
    if log.user:
        user = UserType(
            id=str(log.user.public_id),
            email=log.user.email,
            username=log.user.username,
            is_active=log.user.is_active,
            is_superuser=log.user.is_superuser
        )
    
    return KeyLogType(
        id=log.id,
        key_id=log.key_id,
        user_id=log.user_id,
        user=user,
        action=action_map.get(log.action.value, KeyActionTypeEnum.UPDATE_KEY),
        field_name=log.field_name,
        language=log.language,
        old_value=log.old_value,
        new_value=log.new_value,
        created_at=log.created_at
    )


@strawberry.type
class KeyQuery:
    """
    GraphQL queries for keys.
    """

    @strawberry.field
    def project_keys(self, info: Info, project_id: str) -> List[KeyType]:
        """
        Get all keys for a project.
        
        Args:
            info: GraphQL info object
            project_id: Project UUID
            
        Returns:
            List of keys
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        try:
            current_user_id = get_current_user_id(info)
            if not current_user_id:
                raise UnauthorizedError("Authentication required to access keys")
            
            db: Session = next(get_db())
            try:
                keys = KeyService.get_project_keys(db, project_id, current_user_id)
                if keys is None:
                    return []
                
                return [build_key_type(key) for key in keys]
            finally:
                db.close()
        except UnauthorizedError:
            raise
        except Exception as e:
            logger.error(f"Error in project_keys query: {type(e).__name__}: {str(e)}")
            return []

    @strawberry.field
    def key(self, info: Info, id: str) -> Optional[KeyType]:
        """
        Get a specific key by ID.
        
        Args:
            info: GraphQL info object
            id: Key UUID
            
        Returns:
            Key or None
        """
        try:
            current_user_id = get_current_user_id(info)
            if not current_user_id:
                return None
            
            db: Session = next(get_db())
            try:
                key = KeyService.get_key_by_public_id(db, id)
                if not key:
                    return None
                
                # Check access through project
                from app.services.project_service import ProjectService
                if not ProjectService.check_project_access(db, key.project_id, current_user_id):
                    return None
                
                return build_key_type(key)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in key query: {type(e).__name__}: {str(e)}")
            return None

    @strawberry.field
    def check_key_exists(self, info: Info, project_id: str, key: str) -> bool:
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
            current_user_id = get_current_user_id(info)
            if not current_user_id:
                raise UnauthorizedError("Authentication required to check keys")
            
            db: Session = next(get_db())
            try:
                exists = KeyService.check_key_exists(db, project_id, key, current_user_id)
                if exists is None:
                    return False
                
                return exists
            finally:
                db.close()
        except UnauthorizedError:
            raise
        except Exception as e:
            logger.error(f"Error in check_key_exists query: {type(e).__name__}: {str(e)}")
            return False

    @strawberry.field
    def key_logs(self, info: Info, key_id: str, limit: Optional[int] = 50) -> List[KeyLogType]:
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
            current_user_id = get_current_user_id(info)
            if not current_user_id:
                raise UnauthorizedError("Authentication required to view logs")
            
            db: Session = next(get_db())
            try:
                # Get key to check access
                key = KeyService.get_key_by_public_id(db, key_id, eager_load_translations=False)
                if not key:
                    return []
                
                # Check access through project
                from app.services.project_service import ProjectService
                if not ProjectService.check_project_access(db, key.project_id, current_user_id):
                    raise UnauthorizedError("You don't have access to this key")
                
                # Get logs with eager loading of user
                from app.models.key_log import KeyLog
                logs = db.query(KeyLog).options(
                    joinedload(KeyLog.user)
                ).filter(
                    KeyLog.key_id == key.id
                ).order_by(KeyLog.created_at.desc(), KeyLog.id.desc()).limit(limit or 50).all()
                
                return [build_key_log_type(log) for log in logs]
            finally:
                db.close()
        except UnauthorizedError:
            raise
        except Exception as e:
            logger.error(f"Error in key_logs query: {type(e).__name__}: {str(e)}")
            return []


@strawberry.type
class KeyMutation:
    """
    GraphQL mutations for keys.
    """

    @strawberry.mutation
    def create_key(self, input: CreateKeyInput, info: Info) -> Optional[KeyType]:
        """
        Create a new key.
        
        Args:
            input: Key creation input
            info: GraphQL info object
            
        Returns:
            Created key
            
        Raises:
            UnauthorizedError: If user is not authenticated
            DatabaseError: If database operation fails
        """
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to create keys")
        
        db: Session = next(get_db())
        
        try:
            key = KeyService.create_key(
                db=db,
                project_public_id=input.project_id,
                key=input.key,
                description=input.description,
                tags=input.tags,
                translations=input.translations,
                user_id=current_user_id
            )
            
            if not key:
                return None
            
            return build_key_type(key)
        except (UnauthorizedError, AuthenticationError):
            raise
        except (IntegrityError, OperationalError) as e:
            handle_database_exception(e, "key creation")
        except Exception as e:
            handle_database_exception(e, "key creation")
        finally:
            db.close()

    @strawberry.mutation
    def update_key(self, input: UpdateKeyInput, info: Info) -> Optional[KeyType]:
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
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to update keys")
        
        db: Session = next(get_db())
        
        try:
            key = KeyService.update_key(
                db=db,
                public_id=input.id,
                key=input.key,
                description=input.description,
                tags=input.tags,
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
        finally:
            db.close()

    @strawberry.mutation
    def delete_key(self, id: str, info: Info) -> bool:
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
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to delete keys")
        
        db: Session = next(get_db())
        
        try:
            return KeyService.delete_key(db, id, current_user_id)
        except (UnauthorizedError, AuthenticationError):
            raise
        except (IntegrityError, OperationalError) as e:
            handle_database_exception(e, "key deletion")
        except Exception as e:
            handle_database_exception(e, "key deletion")
        finally:
            db.close()

    @strawberry.mutation
    def set_translation(self, input: SetTranslationInput, info: Info) -> Optional[TranslationType]:
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
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to set translations")
        
        db: Session = next(get_db())
        
        try:
            translation = KeyService.set_translation(
                db=db,
                key_public_id=input.key_id,
                language=input.language,
                value=input.value,
                user_id=current_user_id
            )
            
            if not translation:
                return None
            
            return TranslationType(
                language=translation.language,
                value=translation.value,
                created_at=translation.created_at,
                updated_at=translation.updated_at
            )
        except (UnauthorizedError, AuthenticationError):
            raise
        except (IntegrityError, OperationalError) as e:
            handle_database_exception(e, "translation update")
        except Exception as e:
            handle_database_exception(e, "translation update")
        finally:
            db.close()

    @strawberry.mutation
    def delete_translation(self, input: DeleteTranslationInput, info: Info) -> bool:
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
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to delete translations")
        
        db: Session = next(get_db())
        
        try:
            return KeyService.delete_translation(
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
        finally:
            db.close()

    @strawberry.mutation
    def batch_import_translations(self, input: BatchImportInput, info: Info) -> BatchImportResult:
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
        current_user_id = get_current_user_id(info)
        if not current_user_id:
            raise UnauthorizedError("User must be authenticated to import translations")
        
        db: Session = next(get_db())
        
        try:
            result = KeyService.batch_import_translations(
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
        finally:
            db.close()

