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
        tags: Optional[List[str]] = None,
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
            tags: Optional list of tag strings
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
            tags=tags or [],
            project_id=project.id
        )
        db.add(new_key)
        db.flush()  # Flush to get the ID
        
        # Update project's available_tags
        if tags:
            KeyService._update_project_available_tags(db, project, tags)
        
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
    def check_key_exists(db: Session, project_public_id: str, key: str, user_id: int) -> Optional[bool]:
        """
        Check if a key already exists in a project.
        
        Args:
            db: Database session
            project_public_id: Public UUID of the project
            key: Translation key string to check
            user_id: User ID requesting the check
            
        Returns:
            True if key exists, False if not, None if no access
        """
        # Get project
        project = ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return None
        
        # Check access
        if not ProjectService.check_project_access(db, project.id, user_id):
            return None
        
        # Check if key exists
        existing_key = db.query(Key).filter(
            Key.project_id == project.id,
            Key.key == key
        ).first()
        
        return existing_key is not None

    @staticmethod
    def update_key(
        db: Session,
        public_id: str,
        key: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        user_id: int = None
    ) -> Optional[Key]:
        """
        Update a translation key.
        
        Args:
            db: Database session
            public_id: Public UUID of the key
            key: New key string
            description: New description
            tags: New tags list
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
        
        if tags is not None:
            key_obj.tags = tags
            # Update project's available_tags
            project = db.query(Project).filter(Project.id == key_obj.project_id).first()
            if project:
                KeyService._update_project_available_tags(db, project, tags)
        
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
        If value is empty, deletes the translation.
        
        Args:
            db: Database session
            key_public_id: Public UUID of the key
            language: Language code
            value: Translation value (empty string to delete)
            user_id: User ID setting the translation
            
        Returns:
            Created/updated translation or None if deleted/failed
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
        
        # If value is empty, delete the translation
        if not value or not value.strip():
            if translation:
                db.delete(translation)
                db.commit()
            return None
        
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

    @staticmethod
    def batch_import_translations(
        db: Session,
        project_public_id: str,
        language: str,
        translations: List,
        strategy: str = "merge",
        user_id: int = None
    ) -> Dict:
        """
        Batch import translations for a specific language.
        
        Args:
            db: Database session
            project_public_id: Public UUID of the project
            language: Language code
            translations: List of {key: str, value: str}
            strategy: 'merge' or 'replace'
            user_id: User ID importing translations
            
        Returns:
            Dict with success_count, error_count, created_keys, updated_keys, errors
        """
        from app.services.project_service import ProjectService
        
        # Get project
        project = ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return {
                'success_count': 0,
                'error_count': len(translations),
                'created_keys': 0,
                'updated_keys': 0,
                'errors': ['Project not found']
            }
        
        # Check permission
        if user_id and not ProjectService.can_user_edit_project(db, project.id, user_id):
            return {
                'success_count': 0,
                'error_count': len(translations),
                'created_keys': 0,
                'updated_keys': 0,
                'errors': ['User does not have permission to edit this project']
            }
        
        success_count = 0
        error_count = 0
        created_keys = 0
        updated_keys = 0
        errors = []
        
        try:
            # Get all existing keys for the project
            existing_keys = db.query(Key).filter(
                Key.project_id == project.id
            ).all()
            existing_keys_dict = {k.key: k for k in existing_keys}
            
            # Process each translation
            for trans_input in translations:
                try:
                    key_str = trans_input.key
                    value = trans_input.value
                    
                    # Check if key exists
                    if key_str in existing_keys_dict:
                        # Update existing key's translation
                        key_obj = existing_keys_dict[key_str]
                        
                        # Check if translation exists
                        translation = db.query(Translation).filter(
                            Translation.key_id == key_obj.id,
                            Translation.language == language
                        ).first()
                        
                        if translation:
                            translation.value = value
                        else:
                            translation = Translation(
                                key_id=key_obj.id,
                                language=language,
                                value=value
                            )
                            db.add(translation)
                        
                        updated_keys += 1
                    else:
                        # Create new key with translation
                        new_key = Key(
                            key=key_str,
                            project_id=project.id
                        )
                        db.add(new_key)
                        db.flush()  # Get the ID
                        
                        # Create translation
                        translation = Translation(
                            key_id=new_key.id,
                            language=language,
                            value=value
                        )
                        db.add(translation)
                        
                        # Add to dict for future lookups in this batch
                        existing_keys_dict[key_str] = new_key
                        created_keys += 1
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Error processing key '{trans_input.key}': {str(e)}")
            
            # Commit all changes
            db.commit()
            
        except Exception as e:
            db.rollback()
            return {
                'success_count': 0,
                'error_count': len(translations),
                'created_keys': 0,
                'updated_keys': 0,
                'errors': [f"Batch import failed: {str(e)}"]
            }
        
        return {
            'success_count': success_count,
            'error_count': error_count,
            'created_keys': created_keys,
            'updated_keys': updated_keys,
            'errors': errors
        }

    @staticmethod
    def _update_project_available_tags(db: Session, project: Project, new_tags: List[str]) -> None:
        """
        Update project's available_tags to include new tags.
        
        Args:
            db: Database session
            project: Project instance
            new_tags: List of new tags to add
        """
        if not new_tags:
            return
        
        current_tags = set(project.available_tags or [])
        updated = False
        
        for tag in new_tags:
            if tag and tag not in current_tags:
                current_tags.add(tag)
                updated = True
        
        if updated:
            project.available_tags = sorted(list(current_tags))
            db.commit()

