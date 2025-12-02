from typing import Optional, List, Dict, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_, func
from sqlalchemy.orm import joinedload
import uuid as uuid_lib
import logging

from app.models.key import Key, Translation, ReviewStatus
from app.models.activity_log import ActivityLog, ActionType
from app.models.project import Project
from app.services.project_service import ProjectService
from app.services.ai_service import ai_service
from app.constants.languages import get_language_name

logger = logging.getLogger(__name__)


class KeyService:
    """
    Service for managing translation keys and their translations.
    """

    @staticmethod
    async def _create_log(
        db: AsyncSession,
        key_id: int,
        user_id: Optional[int],
        action: ActionType,
        field_name: Optional[str] = None,
        language: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        project_id: Optional[int] = None
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
            project_id: ID of the project (optional, will be fetched from key if not provided)
        """
        # Get project_id from key if not provided
        if project_id is None and key_id is not None:
            result = await db.execute(select(Key).where(Key.id == key_id))
            key = result.scalar_one_or_none()
            if key:
                project_id = key.project_id
        
        log_entry = ActivityLog(
            key_id=key_id,
            project_id=project_id,
            user_id=user_id,
            action=action,
            field_name=field_name,
            language=language,
            old_value=old_value,
            new_value=new_value
        )
        db.add(log_entry)

    @staticmethod
    async def create_key(
        db: AsyncSession,
        project_public_id: str,
        key: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_plural: bool = False,
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
            is_plural: Whether this key uses plural forms
            translations: Optional dict of {language: translation_value}
            user_id: User ID creating the key (for permission check)
            
        Returns:
            Created key or None if failed
        """
        # Get project
        project = await ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return None
        
        # Check if user has edit permission
        if user_id and not await ProjectService.can_user_edit_project(db, project.id, user_id):
            return None
        
        # Check if key already exists in project
        result = await db.execute(
            select(Key).where(
                Key.project_id == project.id,
                Key.key == key
            )
        )
        existing_key = result.scalar_one_or_none()
        
        if existing_key:
            logger.warning(
                f"Attempt to create duplicate key: "
                f"project_id={project.id}, key='{key}', "
                f"existing_key_id={existing_key.id}"
            )
            return None
        
        # Create key
        new_key = Key(
            key=key,
            description=description,
            tags=tags or [],
            is_plural=is_plural or False,
            project_id=project.id
        )
        db.add(new_key)
        await db.flush()  # Flush to get the ID
        
        # Log key creation
        await KeyService._create_log(
            db=db,
            key_id=new_key.id,
            user_id=user_id,
            action=ActionType.KEY_CREATE,
            field_name="key",
            new_value=key,
            project_id=project.id
        )
        
        # Update project's available_tags
        if tags:
            await KeyService._update_project_available_tags(db, project, tags)
        
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
                await KeyService._create_log(
                    db=db,
                    key_id=new_key.id,
                    user_id=user_id,
                    action=ActionType.TRANSLATION_UPDATE,
                    field_name="translation",
                    language=language,
                    new_value=value,
                    project_id=project.id
                )
        
        await db.commit()
        # Reload full object with translations to avoid detached state issues
        result = await db.execute(
            select(Key)
            .options(joinedload(Key.translations))
            .where(Key.id == new_key.id)
        )
        return result.unique().scalar_one()

    @staticmethod
    async def autopilot_translate(
        db: AsyncSession,
        key: Key,
        source_text: str,
        source_language: str,
        project: Project,
        user_id: Optional[int] = None,
        context: Optional[str] = None
    ) -> Tuple[int, int, List[str]]:
        """
        Automatically translate text to all project languages using AI.
        
        Args:
            db: Database session
            key: Key object to add translations to
            source_text: Text to translate (from default language)
            source_language: Source language code
            project: Project object with language configuration
            user_id: User ID for logging
            context: Optional context for translation (e.g., key description)
            
        Returns:
            Tuple of (success_count, error_count, error_messages)
        """
        success_count = 0
        error_count = 0
        errors: List[str] = []
        
        # Get project languages (excluding source language)
        project_languages = project.languages or []
        target_languages = [
            lang for lang in project_languages 
            if lang.get('code') != source_language
        ]
        
        if not target_languages:
            logger.info(f"No target languages for autopilot translation (key_id={key.id})")
            return (0, 0, [])
        
        source_language_name = get_language_name(source_language)
        
        for lang_config in target_languages:
            lang_code = lang_config.get('code')
            if not lang_code:
                continue
                
            # Check if translation already exists
            result = await db.execute(
                select(Translation).where(
                    Translation.key_id == key.id,
                    Translation.language == lang_code
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                logger.debug(f"Translation already exists for {lang_code}, skipping")
                continue
            
            target_language_name = get_language_name(lang_code)
            
            try:
                # Perform AI translation
                translated_text, reason = await ai_service.translate(
                    text=source_text,
                    target_language=target_language_name,
                    source_language=source_language_name,
                    context=context
                )
                
                if reason or not translated_text:
                    error_msg = f"Failed to translate to {lang_code}: {reason or 'Empty result'}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                    error_count += 1
                    continue
                
                # Create translation
                translation = Translation(
                    key_id=key.id,
                    language=lang_code,
                    value=translated_text
                )
                db.add(translation)
                
                # Log translation creation as AI-generated
                await KeyService._create_log(
                    db=db,
                    key_id=key.id,
                    user_id=user_id,
                    action=ActionType.TRANSLATION_AI_UPDATE,
                    field_name="translation",
                    language=lang_code,
                    new_value=translated_text,
                    project_id=project.id
                )
                
                success_count += 1
                logger.info(f"Autopilot translated to {lang_code} for key_id={key.id}")
                
            except Exception as e:
                error_msg = f"Error translating to {lang_code}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                error_count += 1
        
        if success_count > 0:
            await db.commit()
        
        return (success_count, error_count, errors)

    @staticmethod
    async def get_key_by_public_id(db: AsyncSession, public_id: str, eager_load_translations: bool = True) -> Optional[Key]:
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
            query = select(Key).where(Key.public_id == uuid_obj)
            if eager_load_translations:
                query = query.options(joinedload(Key.translations))
            result = await db.execute(query)
            return result.unique().scalar_one_or_none()
        except (ValueError, AttributeError):
            return None

    @staticmethod
    async def get_project_keys(db: AsyncSession, project_public_id: str, user_id: int) -> Optional[List[Key]]:
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
        project = await ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return None
        
        # Check access
        if not await ProjectService.check_project_access(db, project.id, user_id):
            return None
        
        # Get all keys for the project with eager loading of translations
        # This prevents N+1 query problem by loading translations in a single query
        result = await db.execute(
            select(Key)
            .options(joinedload(Key.translations))
            .where(Key.project_id == project.id)
            .order_by(Key.key)
        )
        keys = result.scalars().unique().all()
        return list(keys)

    @staticmethod
    async def get_project_keys_paginated(
        db: AsyncSession, 
        project_public_id: str, 
        user_id: int,
        offset: int = 0,
        limit: int = 50,
        search: Optional[str] = None
    ) -> Optional[Dict[str, any]]:
        """
        Get keys for a project with pagination and optional search.
        
        Args:
            db: Database session
            project_public_id: Public UUID of the project
            user_id: User ID requesting the keys
            offset: Number of keys to skip
            limit: Maximum number of keys to return
            search: Optional search query to filter keys by key name, description or translation values
            
        Returns:
            Dict with 'keys' list, 'total_count' int, or None if no access
        """
        # Get project
        project = await ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return None
        
        # Check access
        if not await ProjectService.check_project_access(db, project.id, user_id):
            return None
        
        # Apply search filter if provided
        if search and search.strip():
            search_term = f"%{search.strip()}%"
            # Search in key name, description, and translation values
            from app.models.key import Translation
            
            # Build search filter conditions
            search_filter = or_(
                Key.key.ilike(search_term),
                Key.description.ilike(search_term)
            )
            
            # For translation search, we need a subquery to find keys with matching translations
            subq_result = await db.execute(
                select(Translation.key_id.distinct()).where(
                    Translation.value.ilike(search_term)
                )
            )
            translation_key_ids = [row[0] for row in subq_result.all()]
            
            # Combine filters: match by key/description OR by translation
            if translation_key_ids:
                base_filter = (
                    (Key.project_id == project.id) &
                    (search_filter | Key.id.in_(translation_key_ids))
                )
            else:
                base_filter = (
                    (Key.project_id == project.id) & search_filter
                )
            
            # Get total count of matching keys
            count_result = await db.execute(
                select(func.count(Key.id)).where(base_filter)
            )
            total_count = count_result.scalar() or 0
            
            # Get paginated keys with eager loading of translations
            result = await db.execute(
                select(Key)
                .options(joinedload(Key.translations))
                .where(base_filter)
                .order_by(Key.key)
                .offset(offset)
                .limit(limit)
            )
            keys = result.scalars().unique().all()
        else:
            # No search - use simple query
            # Get total count
            count_result = await db.execute(
                select(func.count(Key.id)).where(Key.project_id == project.id)
            )
            total_count = count_result.scalar() or 0
            
            # Get paginated keys with eager loading of translations
            result = await db.execute(
                select(Key)
                .options(joinedload(Key.translations))
                .where(Key.project_id == project.id)
                .order_by(Key.key)
                .offset(offset)
                .limit(limit)
            )
            keys = result.scalars().unique().all()
        
        return {
            'keys': list(keys),
            'total_count': total_count
        }

    @staticmethod
    async def check_key_exists(db: AsyncSession, project_public_id: str, key: str, user_id: int) -> Optional[bool]:
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
        project = await ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return None
        
        # Check access
        if not await ProjectService.check_project_access(db, project.id, user_id):
            return None
        
        # Check if key exists
        result = await db.execute(
            select(Key).where(
                Key.project_id == project.id,
                Key.key == key
            )
        )
        existing_key = result.scalar_one_or_none()
        
        return existing_key is not None

    @staticmethod
    async def update_key(
        db: AsyncSession,
        public_id: str,
        key: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_plural: Optional[bool] = None,
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
            is_plural: Whether this key uses plural forms
            user_id: User ID updating the key
            
        Returns:
            Updated key or None if failed
        """
        # Get key
        key_obj = await KeyService.get_key_by_public_id(db, public_id)
        if not key_obj:
            return None
        
        # Check permission
        if user_id and not await ProjectService.can_user_edit_project(db, key_obj.project_id, user_id):
            return None
        
        # Update fields
        if key is not None:
            # Check uniqueness
            result = await db.execute(
                select(Key).where(
                    Key.project_id == key_obj.project_id,
                    Key.key == key,
                    Key.id != key_obj.id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                logger.warning(
                    f"Attempt to update key to duplicate name: "
                    f"project_id={key_obj.project_id}, key='{key}', "
                    f"existing_key_id={existing.id}"
                )
                return None
            
            # Log key name change
            old_key = key_obj.key
            key_obj.key = key
            await KeyService._create_log(
                db=db,
                key_id=key_obj.id,
                user_id=user_id,
                action=ActionType.KEY_UPDATE,
                field_name="key",
                old_value=old_key,
                new_value=key
            )
        
        if description is not None:
            # Log description change
            old_description = key_obj.description
            key_obj.description = description
            await KeyService._create_log(
                db=db,
                key_id=key_obj.id,
                user_id=user_id,
                action=ActionType.KEY_UPDATE_DESCRIPTION,
                field_name="description",
                old_value=old_description,
                new_value=description
            )
        
        if tags is not None:
            # Update tags but don't log (metadata)
            key_obj.tags = tags
            # Update project's available_tags
            result = await db.execute(select(Project).where(Project.id == key_obj.project_id))
            project = result.scalar_one_or_none()
            if project:
                await KeyService._update_project_available_tags(db, project, tags)
        
        if is_plural is not None:
            # Update is_plural but don't log (metadata)
            key_obj.is_plural = is_plural
        
        await db.commit()
        # Reload full object with translations to avoid detached state issues
        result = await db.execute(
            select(Key)
            .options(joinedload(Key.translations))
            .where(Key.id == key_obj.id)
        )
        return result.unique().scalar_one()

    @staticmethod
    async def delete_key(db: AsyncSession, public_id: str, user_id: int) -> bool:
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
        key_obj = await KeyService.get_key_by_public_id(db, public_id)
        if not key_obj:
            return False
        
        # Check permission
        if not await ProjectService.can_user_edit_project(db, key_obj.project_id, user_id):
            return False
        
        # Log key deletion
        await KeyService._create_log(
            db=db,
            key_id=key_obj.id,
            user_id=user_id,
            action=ActionType.KEY_DELETE,
            field_name="key",
            old_value=key_obj.key
        )
        
        db.delete(key_obj)
        await db.commit()
        return True

    @staticmethod
    async def set_translation(
        db: AsyncSession,
        key_public_id: str,
        language: str,
        value: str,
        user_id: int,
        is_ai_generated: bool = False
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
            is_ai_generated: Whether this translation was generated by AI
            
        Returns:
            Created/updated translation or None if deleted/failed
        """
        # Get key
        key_obj = await KeyService.get_key_by_public_id(db, key_public_id)
        if not key_obj:
            return None
        
        # Check permission
        if not await ProjectService.can_user_edit_project(db, key_obj.project_id, user_id):
            return None
        
        # Check if translation already exists
        result = await db.execute(
            select(Translation).where(
                Translation.key_id == key_obj.id,
                Translation.language == language
            )
        )
        translation = result.scalar_one_or_none()
        
        # Normalize None to empty string
        if value is None:
            value = ""
        
        # If value is empty or only whitespace, delete the translation
        if not value.strip():
            logger.info(f"Deleting translation for key {key_public_id}, language {language}, value was: '{value}'")
            if translation:
                logger.info(f"Found existing translation to delete: {translation.id}")
                # Log translation deletion
                await KeyService._create_log(
                    db=db,
                    key_id=key_obj.id,
                    user_id=user_id,
                    action=ActionType.TRANSLATION_DELETE,
                    field_name="translation",
                    language=language,
                    old_value=translation.value
                )
                await db.execute(
                    delete(Translation).where(Translation.id == translation.id)
                )
                await db.commit()
                logger.info("Translation deleted and committed")
            else:
                logger.info("No existing translation found to delete")
            return None
        
        # Determine action type based on AI generation
        action_type = ActionType.TRANSLATION_AI_UPDATE if is_ai_generated else ActionType.TRANSLATION_UPDATE
        
        if translation:
            # Update existing
            old_value = translation.value
            translation.value = value
            
            # Log translation update
            await KeyService._create_log(
                db=db,
                key_id=key_obj.id,
                user_id=user_id,
                action=action_type,
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
            await KeyService._create_log(
                db=db,
                key_id=key_obj.id,
                user_id=user_id,
                action=action_type,
                field_name="translation",
                language=language,
                new_value=value
            )
        
        # Reset review status to PENDING when translation is updated
        if translation.review_status in [ReviewStatus.APPROVED, ReviewStatus.REJECTED]:
            translation.review_status = ReviewStatus.PENDING
        
        await db.commit()
        await db.refresh(translation)
        return translation

    @staticmethod
    async def delete_translation(
        db: AsyncSession,
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
        key_obj = await KeyService.get_key_by_public_id(db, key_public_id)
        if not key_obj:
            return False
        
        # Check permission
        if not await ProjectService.can_user_edit_project(db, key_obj.project_id, user_id):
            return False
        
        # Find translation
        result = await db.execute(
            select(Translation).where(
                Translation.key_id == key_obj.id,
                Translation.language == language
            )
        )
        translation = result.scalar_one_or_none()
        
        if not translation:
            return False
        
        # Log translation deletion
        await KeyService._create_log(
            db=db,
            key_id=key_obj.id,
            user_id=user_id,
            action=ActionType.TRANSLATION_DELETE,
            field_name="translation",
            language=language,
            old_value=translation.value
        )
        
        db.delete(translation)
        await db.commit()
        return True

    @staticmethod
    async def batch_import_translations(
        db: AsyncSession,
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
        project = await ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return {
                'success_count': 0,
                'error_count': len(translations),
                'created_keys': 0,
                'updated_keys': 0,
                'errors': ['Project not found']
            }
        
        # Check permission
        if user_id and not await ProjectService.can_user_edit_project(db, project.id, user_id):
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
            result = await db.execute(
                select(Key)
                .options(joinedload(Key.translations))
                .where(Key.project_id == project.id)
            )
            existing_keys = result.scalars().unique().all()
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
                        result = await db.execute(
                            select(Translation).where(
                                Translation.key_id == key_obj.id,
                                Translation.language == language
                            )
                        )
                        translation = result.scalar_one_or_none()
                        
                        if translation:
                            old_value = translation.value
                            translation.value = value
                            
                            # Log translation import
                            await KeyService._create_log(
                                db=db,
                                key_id=key_obj.id,
                                user_id=user_id,
                                action=ActionType.TRANSLATION_IMPORT,
                                field_name="translation",
                                language=language,
                                old_value=old_value,
                                new_value=value,
                                project_id=project.id
                            )
                        else:
                            translation = Translation(
                                key_id=key_obj.id,
                                language=language,
                                value=value
                            )
                            db.add(translation)
                            
                            # Log translation import
                            await KeyService._create_log(
                                db=db,
                                key_id=key_obj.id,
                                user_id=user_id,
                                action=ActionType.TRANSLATION_IMPORT,
                                field_name="translation",
                                language=language,
                                new_value=value,
                                project_id=project.id
                            )
                        
                        updated_keys += 1
                    else:
                        # Create new key with translation
                        new_key = Key(
                            key=key_str,
                            project_id=project.id
                        )
                        db.add(new_key)
                        await db.flush()  # Get the ID
                        
                        # Log key creation
                        await KeyService._create_log(
                            db=db,
                            key_id=new_key.id,
                            user_id=user_id,
                            action=ActionType.KEY_CREATE,
                            field_name="key",
                            new_value=key_str,
                            project_id=project.id
                        )
                        
                        # Create translation
                        translation = Translation(
                            key_id=new_key.id,
                            language=language,
                            value=value
                        )
                        db.add(translation)
                        
                        # Log translation import
                        await KeyService._create_log(
                            db=db,
                            key_id=new_key.id,
                            user_id=user_id,
                            action=ActionType.TRANSLATION_IMPORT,
                            field_name="translation",
                            language=language,
                            new_value=value,
                            project_id=project.id
                        )
                        
                        # Add to dict for future lookups in this batch
                        existing_keys_dict[key_str] = new_key
                        created_keys += 1
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Error processing key '{trans_input.key}': {str(e)}")
            
            # Commit all changes
            await db.commit()
            
            # Log batch import summary
            if success_count > 0:
                import_summary = ActivityLog(
                    team_id=project.team_id,
                    project_id=project.id,
                    user_id=user_id,
                    action=ActionType.KEYS_BATCH_IMPORT,
                    field_name="batch_import",
                    language=language,
                    extra_data={
                        "created_keys": created_keys,
                        "updated_keys": updated_keys,
                        "total_processed": success_count,
                        "error_count": error_count
                    }
                )
                db.add(import_summary)
                await db.commit()
            
        except Exception as e:
            await db.rollback()
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
    async def approve_translation(
        db: AsyncSession,
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
        result = await db.execute(
            select(Key).where(Key.public_id == uuid_lib.UUID(key_public_id))
        )
        key = result.scalar_one_or_none()
        
        if not key:
            return None
        
        # Find translation
        result = await db.execute(
            select(Translation).where(
                Translation.key_id == key.id,
                Translation.language == language
            )
        )
        translation = result.scalar_one_or_none()
        
        if not translation:
            return None
        
        # Don't allow approving already approved translation
        if translation.review_status == ReviewStatus.APPROVED:
            return None
        
        old_status = translation.review_status.value
        translation.review_status = ReviewStatus.APPROVED
        
        # Create log entry with language
        await KeyService._create_log(
            db=db,
            key_id=key.id,
            user_id=user_id,
            action=ActionType.REVIEW_APPROVE,
            field_name="review_status",
            language=language,  # Include language in log
            old_value=old_status,
            new_value=comment  # Store comment in new_value field
        )
        
        await db.commit()
        # Reload full object with translations
        result = await db.execute(
            select(Key)
            .options(joinedload(Key.translations))
            .where(Key.id == key.id)
        )
        return result.unique().scalar_one()

    @staticmethod
    async def reject_translation(
        db: AsyncSession,
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
        result = await db.execute(
            select(Key).where(Key.public_id == uuid_lib.UUID(key_public_id))
        )
        key = result.scalar_one_or_none()
        
        if not key:
            return None
        
        # Find translation
        result = await db.execute(
            select(Translation).where(
                Translation.key_id == key.id,
                Translation.language == language
            )
        )
        translation = result.scalar_one_or_none()
        
        if not translation:
            return None
        
        # Don't allow rejecting already rejected translation
        if translation.review_status == ReviewStatus.REJECTED:
            return None
        
        old_status = translation.review_status.value
        translation.review_status = ReviewStatus.REJECTED
        
        # Create log entry with language
        await KeyService._create_log(
            db=db,
            key_id=key.id,
            user_id=user_id,
            action=ActionType.REVIEW_REJECT,
            field_name="review_status",
            language=language,  # Include language in log
            old_value=old_status,
            new_value=comment  # Store comment in new_value field
        )
        
        await db.commit()
        # Reload full object with translations
        result = await db.execute(
            select(Key)
            .options(joinedload(Key.translations))
            .where(Key.id == key.id)
        )
        return result.unique().scalar_one()

    @staticmethod
    async def delete_translation_review(
        db: AsyncSession,
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
        result = await db.execute(
            select(Key).where(Key.public_id == uuid_lib.UUID(key_public_id))
        )
        key = result.scalar_one_or_none()
        
        if not key:
            return None
        
        # Find translation
        result = await db.execute(
            select(Translation).where(
                Translation.key_id == key.id,
                Translation.language == language
            )
        )
        translation = result.scalar_one_or_none()
        
        if not translation:
            return None
        
        old_status = translation.review_status.value
        translation.review_status = ReviewStatus.PENDING
        
        # Create log entry with language
        await KeyService._create_log(
            db=db,
            key_id=key.id,
            user_id=user_id,
            action=ActionType.REVIEW_DELETE,
            field_name="review_status",
            language=language,  # Include language in log
            old_value=old_status,
            new_value=None  # No comment for delete action
        )
        
        await db.commit()
        # Reload full object with translations
        result = await db.execute(
            select(Key)
            .options(joinedload(Key.translations))
            .where(Key.id == key.id)
        )
        return result.unique().scalar_one()

    @staticmethod
    async def _update_project_available_tags(db: AsyncSession, project: Project, new_tags: List[str]) -> None:
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
            await db.commit()

