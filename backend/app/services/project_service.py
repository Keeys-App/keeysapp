from typing import Optional, List
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
import uuid as uuid_lib
import logging

from app.models.project import Project, ProjectMember
from app.models.project_access import ProjectAccess
from app.models.team import Team
from app.models.user import User
from app.models.key import Key, Translation

logger = logging.getLogger(__name__)


class ProjectService:
    """
    Service for managing projects and project memberships.
    """

    @staticmethod
    def create_project(
        db: Session,
        owner_id: int,
        team_id: int,
        name: str,
        description: Optional[str] = None,
        languages: Optional[List] = None,
        default_language: Optional[str] = None,
        color: str = "#6366f1",
        status: str = "active"
    ) -> Project:
        """
        Create a new project in a team.
        
        Args:
            db: Database session
            owner_id: ID of the project owner
            team_id: ID of the team this project belongs to
            name: Project name
            description: Project description
            languages: List of language configurations (dict with code and locale)
            default_language: Default language code (must be in languages list)
            color: Hex color code for the project
            status: Project status (active, archived, draft)
            
        Returns:
            Created project
        """
        if languages is None:
            languages = []
        
        # Convert LanguageConfigInput to dict format for JSON storage
        languages_data = []
        for lang in languages:
            if hasattr(lang, 'code') and hasattr(lang, 'locale'):
                # It's a LanguageConfigInput object
                languages_data.append({
                    'code': lang.code,
                    'locale': lang.locale,
                    'direction': getattr(lang, 'direction', 'ltr')
                })
            elif isinstance(lang, dict):
                # It's already a dict
                languages_data.append(lang)
            
        project = Project(
            name=name,
            description=description,
            languages=languages_data,
            default_language=default_language,
            color=color,
            status=status,
            owner_id=owner_id,
            team_id=team_id
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_project_by_public_id(db: Session, public_id: str) -> Optional[Project]:
        """
        Get a project by its public UUID.
        Uses eager loading to prevent N+1 query problems.
        Note: Does not load keys/translations - use get_projects_stats() for statistics.
        
        Args:
            db: Database session
            public_id: Public UUID of the project
            
        Returns:
            Project or None
        """
        try:
            uuid_obj = uuid_lib.UUID(public_id)
            # Eager load related data except keys/translations (they're heavy and calculated via SQL)
            return db.query(Project).options(
                joinedload(Project.owner),
                joinedload(Project.team),
                selectinload(Project.access_members).joinedload(ProjectAccess.user)
            ).filter(Project.public_id == uuid_obj).first()
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def get_projects_stats(db: Session, project_ids: List[int]) -> dict:
        """
        Get translation statistics for multiple projects efficiently using SQL.
        Returns a dictionary mapping project_id to (keys_count, translated_count).
        
        Args:
            db: Database session
            project_ids: List of project IDs
            
        Returns:
            Dict mapping project_id to tuple (keys_count, translations_count)
        """
        if not project_ids:
            return {}
        
        # Get keys count for each project
        keys_stats = db.query(
            Key.project_id,
            func.count(Key.id).label('keys_count')
        ).filter(
            Key.project_id.in_(project_ids)
        ).group_by(
            Key.project_id
        ).all()
        
        # Get translations count for each project
        # Count only non-empty translations (excluding whitespace-only)
        translations_stats = db.query(
            Key.project_id,
            func.count(Translation.id).label('translations_count')
        ).join(
            Translation, Key.id == Translation.key_id
        ).filter(
            Key.project_id.in_(project_ids),
            Translation.value.isnot(None),
            Translation.value != '',
            func.trim(Translation.value) != ''
        ).group_by(
            Key.project_id
        ).all()
        
        # Build result dictionary
        result = {}
        
        # Add keys counts
        for project_id, keys_count in keys_stats:
            result[project_id] = {'keys_count': keys_count, 'translations_count': 0}
        
        # Add translations counts
        for project_id, translations_count in translations_stats:
            if project_id in result:
                result[project_id]['translations_count'] = translations_count
            else:
                result[project_id] = {'keys_count': 0, 'translations_count': translations_count}
        
        return result

    @staticmethod
    def get_language_progress(db: Session, project_id: int) -> dict:
        """
        Get translation progress for each language in the project.
        
        Args:
            db: Database session
            project_id: Internal project ID
            
        Returns:
            Dict mapping language code to progress percentage and counts
        """
        # Get total keys count
        keys_count = db.query(func.count(Key.id)).filter(
            Key.project_id == project_id
        ).scalar() or 0
        
        if keys_count == 0:
            return {}
        
        # Get translations count per language
        language_stats = db.query(
            Translation.language,
            func.count(Translation.id).label('translations_count')
        ).join(
            Key, Translation.key_id == Key.id
        ).filter(
            Key.project_id == project_id,
            Translation.value.isnot(None),
            Translation.value != '',
            func.trim(Translation.value) != ''
        ).group_by(
            Translation.language
        ).all()
        
        # Build result dictionary with progress percentage
        result = {}
        for language, translations_count in language_stats:
            if keys_count > 0:
                # Calculate percentage
                raw_progress = (translations_count / keys_count) * 100
                # If there are translations but percentage rounds to 0, show at least 1%
                if translations_count > 0 and raw_progress < 1:
                    progress = 1
                else:
                    progress = int(raw_progress)
            else:
                progress = 0
            
            result[language] = {
                'progress': progress,
                'completed': translations_count,
                'total': keys_count
            }
        
        return result

    @staticmethod
    def get_user_projects(db: Session, user_id: int) -> List[Project]:
        """
        Get all projects where user is owner or has access through ProjectAccess.
        Uses eager loading to prevent N+1 query problems.
        Note: Does not load keys/translations - use get_projects_stats() for statistics.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of projects
        """
        # Eager load related data except keys/translations (they're heavy and calculated via SQL)
        eager_options = [
            joinedload(Project.owner),
            joinedload(Project.team),
            selectinload(Project.access_members).joinedload(ProjectAccess.user),
        ]
        
        # Get projects where user is owner
        owned_projects = db.query(Project).options(
            *eager_options
        ).filter(
            Project.owner_id == user_id
        ).all()
        owned_project_ids = {p.id for p in owned_projects}
        
        # Get projects where user has access
        access_projects = db.query(Project).options(
            *eager_options
        ).join(
            ProjectAccess, Project.id == ProjectAccess.project_id
        ).filter(
            ProjectAccess.user_id == user_id
        ).all()
        
        # Combine and deduplicate
        all_projects = owned_projects.copy()
        for project in access_projects:
            if project.id not in owned_project_ids:
                all_projects.append(project)
        
        return all_projects

    @staticmethod
    def update_project(
        db: Session,
        public_id: str,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        languages: Optional[List] = None,
        default_language: Optional[str] = None,
        color: Optional[str] = None,
        status: Optional[str] = None
    ) -> Optional[Project]:
        """
        Update a project. Only owner or admin members can update.
        
        Args:
            db: Database session
            public_id: Public UUID of the project
            user_id: User ID requesting the update
            name: New project name
            description: New project description
            languages: New list of language configurations (dict with code and locale)
            default_language: New default language code
            color: New hex color code
            status: New project status
            
        Returns:
            Updated project or None if not found or no permission
        """
        project = ProjectService.get_project_by_public_id(db, public_id)
        if not project:
            return None
        
        # Check if user has permission to update
        if not ProjectService.can_user_edit_project(db, project.id, user_id):
            return None
        
        # Update fields if provided
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if languages is not None:
            # Convert LanguageConfigInput to dict format for JSON storage
            languages_data = []
            for lang in languages:
                if hasattr(lang, 'code') and hasattr(lang, 'locale'):
                    # It's a LanguageConfigInput object
                    languages_data.append({
                        'code': lang.code,
                        'locale': lang.locale,
                        'direction': getattr(lang, 'direction', 'ltr')
                    })
                elif isinstance(lang, dict):
                    # It's already a dict
                    languages_data.append(lang)
            project.languages = languages_data
        if default_language is not None:
            project.default_language = default_language
        if color is not None:
            project.color = color
        if status is not None:
            project.status = status
        
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(db: Session, public_id: str, user_id: int) -> bool:
        """
        Delete a project. Only owner can delete.
        
        Args:
            db: Database session
            public_id: Public UUID of the project
            user_id: User ID requesting the deletion
            
        Returns:
            True if deleted, False otherwise
        """
        project = ProjectService.get_project_by_public_id(db, public_id)
        if not project:
            return False
        
        # Only owner can delete
        if project.owner_id != user_id:
            return False
        
        db.delete(project)
        db.commit()
        return True

    @staticmethod
    def check_project_access(db: Session, project_id: int, user_id: int) -> bool:
        """
        Check if user has access to a project (owner or has ProjectAccess).
        
        Args:
            db: Database session
            project_id: Internal project ID
            user_id: User ID
            
        Returns:
            True if user has access, False otherwise
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return False
        
        # Check if owner
        if project.owner_id == user_id:
            return True
        
        # Check if has project access
        access = db.query(ProjectAccess).filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == user_id
        ).first()
        
        return access is not None

    @staticmethod
    def can_user_edit_project(db: Session, project_id: int, user_id: int) -> bool:
        """
        Check if user can edit a project (owner or admin access).
        
        Args:
            db: Database session
            project_id: Internal project ID
            user_id: User ID
            
        Returns:
            True if user can edit, False otherwise
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return False
        
        # Owner can always edit
        if project.owner_id == user_id:
            return True
        
        # Check if has admin access
        access = db.query(ProjectAccess).filter(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == user_id,
            ProjectAccess.role == "admin"
        ).first()
        
        return access is not None

    @staticmethod
    def add_project_member(
        db: Session,
        project_public_id: str,
        user_public_id: str,
        role: str,
        added_by_user_id: int
    ) -> Optional[ProjectMember]:
        """
        Add a member to a project. Only owner or admin can add members.
        
        Args:
            db: Database session
            project_public_id: Public UUID of the project
            user_public_id: Public UUID of the user to add
            role: Role for the new member (admin, editor, viewer)
            added_by_user_id: User ID who is adding the member
            
        Returns:
            Created ProjectMember or None if failed
        """
        # Get project
        project = ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return None
        
        # Check permission
        if not ProjectService.can_user_edit_project(db, project.id, added_by_user_id):
            return None
        
        # Get user to add
        try:
            uuid_obj = uuid_lib.UUID(user_public_id)
            user = db.query(User).filter(User.public_id == uuid_obj).first()
            if not user:
                return None
        except (ValueError, AttributeError):
            return None
        
        # Check if already a member
        existing_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == user.id
        ).first()
        
        if existing_member:
            # Update role if already exists
            existing_member.role = role
            db.commit()
            db.refresh(existing_member)
            return existing_member
        
        # Create new member
        member = ProjectMember(
            project_id=project.id,
            user_id=user.id,
            role=role
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def remove_project_member(
        db: Session,
        project_public_id: str,
        user_public_id: str,
        removed_by_user_id: int
    ) -> bool:
        """
        Remove a member from a project. Only owner or admin can remove members.
        
        Args:
            db: Database session
            project_public_id: Public UUID of the project
            user_public_id: Public UUID of the user to remove
            removed_by_user_id: User ID who is removing the member
            
        Returns:
            True if removed, False otherwise
        """
        # Get project
        project = ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return False
        
        # Check permission
        if not ProjectService.can_user_edit_project(db, project.id, removed_by_user_id):
            return False
        
        # Get user to remove
        try:
            uuid_obj = uuid_lib.UUID(user_public_id)
            user = db.query(User).filter(User.public_id == uuid_obj).first()
            if not user:
                return False
        except (ValueError, AttributeError):
            return False
        
        # Cannot remove owner
        if project.owner_id == user.id:
            return False
        
        # Find and remove member
        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == user.id
        ).first()
        
        if not member:
            return False
        
        db.delete(member)
        db.commit()
        return True

    @staticmethod
    def transfer_project(
        db: Session,
        project_public_id: str,
        new_team_id: int,
        user_id: int
    ) -> Optional[Project]:
        """
        Transfer a project to another team. Only owner can transfer.
        All ProjectAccess entries are removed when transferring.
        
        Args:
            db: Database session
            project_public_id: Public UUID of the project
            new_team_id: New team ID
            user_id: User ID requesting the transfer (must be owner)
            
        Returns:
            Updated project or None if failed
        """
        project = ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return None
        
        # Only owner can transfer
        if project.owner_id != user_id:
            return None
        
        # Verify new team exists and user has access to it
        team = db.query(Team).filter(Team.id == new_team_id).first()
        if not team:
            return None
        
        # Verify user is owner or member of new team
        from app.services.team_service import TeamService
        if not TeamService.check_user_team_access(db, new_team_id, user_id):
            return None
        
        # Remove all existing project access entries
        db.query(ProjectAccess).filter(ProjectAccess.project_id == project.id).delete()
        
        # Update project team
        project.team_id = new_team_id
        db.commit()
        db.refresh(project)
        
        return project

    @staticmethod
    def export_project_data(db: Session, project_public_id: str, user_id: int) -> Optional[dict]:
        """
        Export project data in i18n format for backup or sharing.
        
        Args:
            db: Database session
            project_public_id: Public UUID of the project
            user_id: User ID requesting the export
            
        Returns:
            Dict with project data or None if no access
        """
        # Get project
        project = ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return None
        
        # Check access
        if not ProjectService.check_project_access(db, project.id, user_id):
            return None
        
        # Get all keys with translations
        keys = db.query(Key).filter(Key.project_id == project.id).all()
        
        # Build keys array with descriptions and tags
        keys_list = []
        for key in keys:
            keys_list.append({
                'key': key.key,
                'description': key.description or '',
                'tags': key.tags or []
            })
        
        # Build locales structure (translations only, no locale duplication)
        locales = []
        for lang in project.languages:
            # lang is always a dict with 'code' and 'locale'
            code = lang.get('code', '')
            
            # Collect translations for this language
            translations = {}
            for key in keys:
                translation = db.query(Translation).filter(
                    Translation.key_id == key.id,
                    Translation.language == code
                ).first()
                
                if translation and translation.value:
                    translations[key.key] = translation.value
            
            locales.append({
                'code': code,
                'keys': translations
            })
        
        return {
            'name': project.name,
            'config': {
                'description': project.description or '',
                'languages': project.languages,
                'defaultLanguage': project.default_language,  # Don't convert None to empty string
                'availableTags': project.available_tags or [],
                'color': project.color,
                'status': project.status
            },
            'keys': keys_list,
            'locales': locales
        }

    @staticmethod
    def import_project_data(
        db: Session,
        owner_id: int,
        team_id: int,
        project_data: dict
    ) -> Optional[Project]:
        """
        Import project data from exported JSON format into a team.
        
        Args:
            db: Database session
            owner_id: ID of the user creating the project
            team_id: ID of the team to import into
            project_data: Dict with project data in export format
            
        Returns:
            Created project or None if failed
        """
        try:
            logger.info(f"Starting import_project_data for owner_id: {owner_id}, team_id: {team_id}")
            
            # Extract project config
            name = project_data.get('name', 'Imported Project')
            config = project_data.get('config', {})
            keys_data = project_data.get('keys', [])
            locales = project_data.get('locales', [])
            
            logger.info(f"Extracted data - name: {name}, keys: {len(keys_data)}, locales: {len(locales)}")
            
            # Get default language and convert empty string to None
            default_language = config.get('defaultLanguage')
            if default_language == '':
                default_language = None
            
            logger.info(f"Creating project with languages: {config.get('languages', [])}")
            
            # Create project
            project = ProjectService.create_project(
                db=db,
                owner_id=owner_id,
                team_id=team_id,
                name=name,
                description=config.get('description'),
                languages=config.get('languages', []),
                default_language=default_language,
                color=config.get('color', '#6366f1'),
                status=config.get('status', 'active')
            )
            
            logger.info(f"Project created: {project.id}")
            
            # Set available_tags if present
            if config.get('availableTags'):
                project.available_tags = config.get('availableTags', [])
                logger.info(f"Set available_tags: {config.get('availableTags')}")
            
            # Import ActivityLog model and action types for logging
            from app.models.activity_log import ActivityLog, ActionType
            
            # Create keys with descriptions and tags first
            logger.info(f"Creating {len(keys_data)} keys")
            created_keys = {}
            for i, key_item in enumerate(keys_data):
                key_str = key_item.get('key')
                description = key_item.get('description', '')
                tags = key_item.get('tags', [])
                
                if not key_str:
                    logger.warning(f"Skipping key {i}: no key string")
                    continue
                
                new_key = Key(
                    key=key_str,
                    description=description,
                    tags=tags,
                    project_id=project.id
                )
                db.add(new_key)
                db.flush()
                created_keys[key_str] = new_key
                
                # Log key import
                log = ActivityLog(
                    key_id=new_key.id,
                    project_id=project.id,
                    user_id=owner_id,
                    action=ActionType.TRANSLATION_IMPORT,
                    field_name="key",
                    new_value=key_str
                )
                db.add(log)
            
            logger.info(f"Created {len(created_keys)} keys successfully")
            
            # Import translations
            logger.info(f"Processing {len(locales)} locales")
            translations_count = 0
            for locale_data in locales:
                language_code = locale_data.get('code')
                translations_data = locale_data.get('keys', {})
                
                if not language_code:
                    logger.warning("Skipping locale: no language code")
                    continue
                
                logger.info(f"Processing locale {language_code} with {len(translations_data)} translations")
                
                # Process each translation
                for key_str, translation_value in translations_data.items():
                    # Get the key (it should exist from the keys array)
                    key_obj = created_keys.get(key_str)
                    
                    if not key_obj:
                        # If key not in keys array, create it without description
                        key_obj = db.query(Key).filter(
                            Key.project_id == project.id,
                            Key.key == key_str
                        ).first()
                        
                        if not key_obj:
                            key_obj = Key(
                                key=key_str,
                                project_id=project.id
                            )
                            db.add(key_obj)
                            db.flush()
                            created_keys[key_str] = key_obj
                            
                            # Log key import
                            log = ActivityLog(
                                key_id=key_obj.id,
                                project_id=project.id,
                                user_id=owner_id,
                                action=ActionType.TRANSLATION_IMPORT,
                                field_name="key",
                                new_value=key_str
                            )
                            db.add(log)
                    
                    # Create translation
                    translation = Translation(
                        key_id=key_obj.id,
                        language=language_code,
                        value=translation_value
                    )
                    db.add(translation)
                    
                    # Log translation import
                    log = ActivityLog(
                        key_id=key_obj.id,
                        project_id=project.id,
                        user_id=owner_id,
                        action=ActionType.TRANSLATION_IMPORT,
                        field_name="translation",
                        language=language_code,
                        new_value=translation_value
                    )
                    db.add(log)
                    
                    translations_count += 1
            
            logger.info(f"Created {translations_count} translations, committing to database")
            db.commit()
            db.refresh(project)
            logger.info(f"Import completed successfully for project: {project.public_id}")
            return project
            
        except Exception as e:
            logger.error(f"Import failed with error: {type(e).__name__}: {str(e)}")
            logger.exception("Full traceback:")
            db.rollback()
            raise e

