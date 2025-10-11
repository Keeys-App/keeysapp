from typing import Optional, List, Dict
from sqlalchemy.orm import Session, joinedload
import uuid as uuid_lib

from app.models.key import Key, Translation, ReviewStatus
from app.models.key_log import KeyLog, KeyActionType
from app.models.project import Project
from app.services.project_service import ProjectService


class KeyService:
    """
    Service for managing translation keys and their translations.
    """

    @staticmethod
    def _create_log(
        db: Session,
        key_id: int,
        user_id: Optional[int],
        action: KeyActionType,
        field_name: Optional[str] = None,
        language: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None
    ) -> None:
        """
        Create a log entry for a key action.
        
        Args:
            db: Database session
            key_id: ID of the key
            user_id: ID of the user performing the action
            action: Type of action
            field_name: Name of the field being changed
            language: Language code (for translations)
            old_value: Old value
            new_value: New value
        """
        log_entry = KeyLog(
            key_id=key_id,
            user_id=user_id,
            action=action,
            field_name=field_name,
            language=language,
            old_value=old_value,
            new_value=new_value
        )
        db.add(log_entry)

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
        
        # Log key creation
        KeyService._create_log(
            db=db,
            key_id=new_key.id,
            user_id=user_id,
            action=KeyActionType.CREATE,
            field_name="key",
            new_value=key
        )
        
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
                
                # Log translation creation
                KeyService._create_log(
                    db=db,
                    key_id=new_key.id,
                    user_id=user_id,
                    action=KeyActionType.UPDATE_TRANSLATION,
                    field_name="translation",
                    language=language,
                    new_value=value
                )
        
        db.commit()
        db.refresh(new_key)
        return new_key

    @staticmethod
    def get_key_by_public_id(db: Session, public_id: str, eager_load_translations: bool = True) -> Optional[Key]:
        """
        Get a key by its public UUID.
        
        Args:
            db: Database session
            public_id: Public UUID of the key
            eager_load_translations: Whether to load translations eagerly (default: True)
            
        Returns:
            Key or None
        """
        try:
            uuid_obj = uuid_lib.UUID(public_id)
            query = db.query(Key)
            if eager_load_translations:
                query = query.options(joinedload(Key.translations))
            return query.filter(Key.public_id == uuid_obj).first()
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
        
        # Get all keys for the project with eager loading of translations
        # This prevents N+1 query problem by loading translations in a single query
        keys = db.query(Key).options(
            joinedload(Key.translations)
        ).filter(Key.project_id == project.id).order_by(Key.key).all()
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
            
            # Log key name change
            old_key = key_obj.key
            key_obj.key = key
            KeyService._create_log(
                db=db,
                key_id=key_obj.id,
                user_id=user_id,
                action=KeyActionType.UPDATE_KEY,
                field_name="key",
                old_value=old_key,
                new_value=key
            )
        
        if description is not None:
            # Log description change
            old_description = key_obj.description
            key_obj.description = description
            KeyService._create_log(
                db=db,
                key_id=key_obj.id,
                user_id=user_id,
                action=KeyActionType.UPDATE_DESCRIPTION,
                field_name="description",
                old_value=old_description,
                new_value=description
            )
        
        if tags is not None:
            # Update tags but don't log (metadata)
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
        
        # Log key deletion
        KeyService._create_log(
            db=db,
            key_id=key_obj.id,
            user_id=user_id,
            action=KeyActionType.DELETE,
            field_name="key",
            old_value=key_obj.key
        )
        
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
        
        # Trim whitespace (spaces, tabs, newlines) from start and end
        value = value.strip() if value else ""
        
        # If value is empty, delete the translation
        if not value:
            if translation:
                # Log translation deletion
                KeyService._create_log(
                    db=db,
                    key_id=key_obj.id,
                    user_id=user_id,
                    action=KeyActionType.DELETE_TRANSLATION,
                    field_name="translation",
                    language=language,
                    old_value=translation.value
                )
                db.delete(translation)
                db.commit()
            return None
        
        if translation:
            # Update existing
            old_value = translation.value
            translation.value = value
            
            # Log translation update
            KeyService._create_log(
                db=db,
                key_id=key_obj.id,
                user_id=user_id,
                action=KeyActionType.UPDATE_TRANSLATION,
                field_name="translation",
                language=language,
                old_value=old_value,
                new_value=value
            )
        else:
            # Create new
            translation = Translation(
                key_id=key_obj.id,
                language=language,
                value=value
            )
            db.add(translation)
            
            # Log translation creation
            KeyService._create_log(
                db=db,
                key_id=key_obj.id,
                user_id=user_id,
                action=KeyActionType.UPDATE_TRANSLATION,
                field_name="translation",
                language=language,
                new_value=value
            )
        
        # Reset review status to PENDING when translation is updated
        if translation.review_status in [ReviewStatus.APPROVED, ReviewStatus.REJECTED]:
            translation.review_status = ReviewStatus.PENDING
        
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
        
        # Log translation deletion
        KeyService._create_log(
            db=db,
            key_id=key_obj.id,
            user_id=user_id,
            action=KeyActionType.DELETE_TRANSLATION,
            field_name="translation",
            language=language,
            old_value=translation.value
        )
        
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
            # Get all existing keys for the project with eager loading
            existing_keys = db.query(Key).options(
                joinedload(Key.translations)
            ).filter(
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
                            old_value = translation.value
                            translation.value = value
                            
                            # Log translation import
                            KeyService._create_log(
                                db=db,
                                key_id=key_obj.id,
                                user_id=user_id,
                                action=KeyActionType.IMPORT,
                                field_name="translation",
                                language=language,
                                old_value=old_value,
                                new_value=value
                            )
                        else:
                            translation = Translation(
                                key_id=key_obj.id,
                                language=language,
                                value=value
                            )
                            db.add(translation)
                            
                            # Log translation import
                            KeyService._create_log(
                                db=db,
                                key_id=key_obj.id,
                                user_id=user_id,
                                action=KeyActionType.IMPORT,
                                field_name="translation",
                                language=language,
                                new_value=value
                            )
                        
                        updated_keys += 1
                    else:
                        # Create new key with translation
                        new_key = Key(
                            key=key_str,
                            project_id=project.id
                        )
                        db.add(new_key)
                        db.flush()  # Get the ID
                        
                        # Log key creation
                        KeyService._create_log(
                            db=db,
                            key_id=new_key.id,
                            user_id=user_id,
                            action=KeyActionType.CREATE,
                            field_name="key",
                            new_value=key_str
                        )
                        
                        # Create translation
                        translation = Translation(
                            key_id=new_key.id,
                            language=language,
                            value=value
                        )
                        db.add(translation)
                        
                        # Log translation import
                        KeyService._create_log(
                            db=db,
                            key_id=new_key.id,
                            user_id=user_id,
                            action=KeyActionType.IMPORT,
                            field_name="translation",
                            language=language,
                            new_value=value
                        )
                        
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
    def approve_translation(
        db: Session,
        key_public_id: str,
        language: str,
        user_id: int,
        comment: Optional[str] = None
    ) -> Optional[Key]:
        """
        Approve a translation.
        
        Args:
            db: Database session
            key_public_id: Public UUID of the key
            language: Language code
            user_id: ID of the user performing the action
            comment: Optional review comment
            
        Returns:
            Updated key or None if not found
        """
        key = db.query(Key).filter(Key.public_id == uuid_lib.UUID(key_public_id)).first()
        
        if not key:
            return None
        
        # Find translation
        translation = db.query(Translation).filter(
            Translation.key_id == key.id,
            Translation.language == language
        ).first()
        
        if not translation:
            return None
        
        # Don't allow approving already approved translation
        if translation.review_status == ReviewStatus.APPROVED:
            return None
        
        old_status = translation.review_status.value
        translation.review_status = ReviewStatus.APPROVED
        
        # Create log entry with language
        KeyService._create_log(
            db=db,
            key_id=key.id,
            user_id=user_id,
            action=KeyActionType.REVIEW_APPROVE,
            field_name="review_status",
            language=language,  # Include language in log
            old_value=old_status,
            new_value=comment  # Store comment in new_value field
        )
        
        db.commit()
        db.refresh(key)
        
        return key

    @staticmethod
    def reject_translation(
        db: Session,
        key_public_id: str,
        language: str,
        user_id: int,
        comment: Optional[str] = None
    ) -> Optional[Key]:
        """
        Reject a translation.
        
        Args:
            db: Database session
            key_public_id: Public UUID of the key
            language: Language code
            user_id: ID of the user performing the action
            comment: Optional review comment
            
        Returns:
            Updated key or None if not found
        """
        key = db.query(Key).filter(Key.public_id == uuid_lib.UUID(key_public_id)).first()
        
        if not key:
            return None
        
        # Find translation
        translation = db.query(Translation).filter(
            Translation.key_id == key.id,
            Translation.language == language
        ).first()
        
        if not translation:
            return None
        
        # Don't allow rejecting already rejected translation
        if translation.review_status == ReviewStatus.REJECTED:
            return None
        
        old_status = translation.review_status.value
        translation.review_status = ReviewStatus.REJECTED
        
        # Create log entry with language
        KeyService._create_log(
            db=db,
            key_id=key.id,
            user_id=user_id,
            action=KeyActionType.REVIEW_REJECT,
            field_name="review_status",
            language=language,  # Include language in log
            old_value=old_status,
            new_value=comment  # Store comment in new_value field
        )
        
        db.commit()
        db.refresh(key)
        
        return key

    @staticmethod
    def delete_translation_review(
        db: Session,
        key_public_id: str,
        language: str,
        user_id: int
    ) -> Optional[Key]:
        """
        Delete review status and reset translation to pending.
        
        Args:
            db: Database session
            key_public_id: Public UUID of the key
            language: Language code
            user_id: ID of the user performing the action
            
        Returns:
            Updated key or None if not found
        """
        key = db.query(Key).filter(Key.public_id == uuid_lib.UUID(key_public_id)).first()
        
        if not key:
            return None
        
        # Find translation
        translation = db.query(Translation).filter(
            Translation.key_id == key.id,
            Translation.language == language
        ).first()
        
        if not translation:
            return None
        
        old_status = translation.review_status.value
        translation.review_status = ReviewStatus.PENDING
        
        # Create log entry with language
        KeyService._create_log(
            db=db,
            key_id=key.id,
            user_id=user_id,
            action=KeyActionType.REVIEW_DELETE,
            field_name="review_status",
            language=language,  # Include language in log
            old_value=old_status,
            new_value=None  # No comment for delete action
        )
        
        db.commit()
        db.refresh(key)
        
        return key

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

