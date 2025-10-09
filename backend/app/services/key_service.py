from typing import Optional, List, Dict
from sqlalchemy.orm import Session
import uuid as uuid_lib

from app.models.key import Key, Translation
from app.models.project import Project
from app.services.project_service import ProjectService


class KeyService:
    """
    Service for managing translation keys and their translations.
    """

    @staticmethod
    def create_key(
        db: Session,
        project_public_id: str,
        key: str,
        description: Optional[str] = None,
        translations: Optional[Dict[str, str]] = None,
        user_id: int = None
    ) -> Optional[Key]:
        """
        Create a new translation key for a project.
        
        Args:
            db: Database session
            project_public_id: Public UUID of the project
            key: Translation key string (e.g., "button.submit")
            description: Optional description for translators
            translations: Optional dict of {language: translation_value}
            user_id: User ID creating the key (for permission check)
            
        Returns:
            Created key or None if failed
        """
        # Get project
        project = ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return None
        
        # Check if user has edit permission
        if user_id and not ProjectService.can_user_edit_project(db, project.id, user_id):
            return None
        
        # Check if key already exists in project
        existing_key = db.query(Key).filter(
            Key.project_id == project.id,
            Key.key == key
        ).first()
        
        if existing_key:
            return None
        
        # Create key
        new_key = Key(
            key=key,
            description=description,
            project_id=project.id
        )
        db.add(new_key)
        db.flush()  # Flush to get the ID
        
        # Create translations if provided
        if translations:
            for language, value in translations.items():
                translation = Translation(
                    key_id=new_key.id,
                    language=language,
                    value=value
                )
                db.add(translation)
        
        db.commit()
        db.refresh(new_key)
        return new_key

    @staticmethod
    def get_key_by_public_id(db: Session, public_id: str) -> Optional[Key]:
        """
        Get a key by its public UUID.
        
        Args:
            db: Database session
            public_id: Public UUID of the key
            
        Returns:
            Key or None
        """
        try:
            uuid_obj = uuid_lib.UUID(public_id)
            return db.query(Key).filter(Key.public_id == uuid_obj).first()
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def get_project_keys(db: Session, project_public_id: str, user_id: int) -> Optional[List[Key]]:
        """
        Get all keys for a project.
        
        Args:
            db: Database session
            project_public_id: Public UUID of the project
            user_id: User ID requesting the keys
            
        Returns:
            List of keys or None if no access
        """
        # Get project
        project = ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return None
        
        # Check access
        if not ProjectService.check_project_access(db, project.id, user_id):
            return None
        
        # Get all keys for the project
        keys = db.query(Key).filter(Key.project_id == project.id).order_by(Key.key).all()
        return keys

    @staticmethod
    def update_key(
        db: Session,
        public_id: str,
        key: Optional[str] = None,
        description: Optional[str] = None,
        user_id: int = None
    ) -> Optional[Key]:
        """
        Update a translation key.
        
        Args:
            db: Database session
            public_id: Public UUID of the key
            key: New key string
            description: New description
            user_id: User ID updating the key
            
        Returns:
            Updated key or None if failed
        """
        # Get key
        key_obj = KeyService.get_key_by_public_id(db, public_id)
        if not key_obj:
            return None
        
        # Check permission
        if user_id and not ProjectService.can_user_edit_project(db, key_obj.project_id, user_id):
            return None
        
        # Update fields
        if key is not None:
            # Check uniqueness
            existing = db.query(Key).filter(
                Key.project_id == key_obj.project_id,
                Key.key == key,
                Key.id != key_obj.id
            ).first()
            
            if existing:
                return None
            
            key_obj.key = key
        
        if description is not None:
            key_obj.description = description
        
        db.commit()
        db.refresh(key_obj)
        return key_obj

    @staticmethod
    def delete_key(db: Session, public_id: str, user_id: int) -> bool:
        """
        Delete a translation key and all its translations.
        
        Args:
            db: Database session
            public_id: Public UUID of the key
            user_id: User ID deleting the key
            
        Returns:
            True if deleted, False otherwise
        """
        # Get key
        key_obj = KeyService.get_key_by_public_id(db, public_id)
        if not key_obj:
            return False
        
        # Check permission
        if not ProjectService.can_user_edit_project(db, key_obj.project_id, user_id):
            return False
        
        db.delete(key_obj)
        db.commit()
        return True

    @staticmethod
    def set_translation(
        db: Session,
        key_public_id: str,
        language: str,
        value: str,
        user_id: int
    ) -> Optional[Translation]:
        """
        Set or update a translation for a key in a specific language.
        
        Args:
            db: Database session
            key_public_id: Public UUID of the key
            language: Language code
            value: Translation value
            user_id: User ID setting the translation
            
        Returns:
            Created/updated translation or None if failed
        """
        # Get key
        key_obj = KeyService.get_key_by_public_id(db, key_public_id)
        if not key_obj:
            return None
        
        # Check permission
        if not ProjectService.can_user_edit_project(db, key_obj.project_id, user_id):
            return None
        
        # Check if translation already exists
        translation = db.query(Translation).filter(
            Translation.key_id == key_obj.id,
            Translation.language == language
        ).first()
        
        if translation:
            # Update existing
            translation.value = value
        else:
            # Create new
            translation = Translation(
                key_id=key_obj.id,
                language=language,
                value=value
            )
            db.add(translation)
        
        db.commit()
        db.refresh(translation)
        return translation

    @staticmethod
    def delete_translation(
        db: Session,
        key_public_id: str,
        language: str,
        user_id: int
    ) -> bool:
        """
        Delete a translation for a key in a specific language.
        
        Args:
            db: Database session
            key_public_id: Public UUID of the key
            language: Language code
            user_id: User ID deleting the translation
            
        Returns:
            True if deleted, False otherwise
        """
        # Get key
        key_obj = KeyService.get_key_by_public_id(db, key_public_id)
        if not key_obj:
            return False
        
        # Check permission
        if not ProjectService.can_user_edit_project(db, key_obj.project_id, user_id):
            return False
        
        # Find translation
        translation = db.query(Translation).filter(
            Translation.key_id == key_obj.id,
            Translation.language == language
        ).first()
        
        if not translation:
            return False
        
        db.delete(translation)
        db.commit()
        return True

