from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import joinedload, selectinload
import uuid as uuid_lib
import logging
import json

from app.models.project import Project, ProjectMember
from app.models.project_access import ProjectAccess
from app.models.team import Team
from app.models.user import User
from app.models.key import Key, Translation
from app.models.activity_log import ActivityLog, ActionType

logger = logging.getLogger(__name__)


class ProjectService:
    """
    Service for managing projects and project memberships.
    """

    @staticmethod
    async def _create_log(
        db: AsyncSession,
        project_id: int,
        user_id: int,
        action: ActionType,
        field_name: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        affected_user_id: Optional[int] = None,
        extra_data: Optional[dict] = None
    ):
        """
        Create an activity log entry for project actions.
        Automatically includes team_id from the project.
        
        Args:
            db: Database session
            project_id: Internal project ID
            user_id: User who performed the action
            action: Type of action
            field_name: Name of the field that changed
            old_value: Previous value
            new_value: New value
            affected_user_id: User affected by the action (for team management)
            extra_data: Additional data as JSON
        """
        # Get team_id from project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        team_id = project.team_id if project else None
        
        log = ActivityLog(
            team_id=team_id,
            project_id=project_id,
            user_id=user_id,
            action=action,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            affected_user_id=affected_user_id,
            extra_data=extra_data
        )
        db.add(log)

    @staticmethod
    async def create_project(
        db: AsyncSession,
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
        await db.flush()
        
        # Log project creation
        await ProjectService._create_log(
            db=db,
            project_id=project.id,
            user_id=owner_id,
            action=ActionType.PROJECT_CREATE,
            field_name="name",
            new_value=name
        )
        
        await db.commit()
        
        # Reload with relationships
        result = await db.execute(
            select(Project)
            .options(
                joinedload(Project.owner),
                joinedload(Project.team),
                selectinload(Project.access_members).joinedload(ProjectAccess.user)
            )
            .where(Project.id == project.id)
        )
        return result.unique().scalar_one()

    @staticmethod
    async def get_project_by_public_id(db: AsyncSession, public_id: str) -> Optional[Project]:
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
            result = await db.execute(
                select(Project)
                .options(
                    joinedload(Project.owner),
                    joinedload(Project.team),
                    selectinload(Project.access_members).joinedload(ProjectAccess.user)
                )
                .where(Project.public_id == uuid_obj)
            )
            return result.unique().scalar_one_or_none()
        except (ValueError, AttributeError):
            return None

    @staticmethod
    async def get_projects_stats(db: AsyncSession, project_ids: List[int]) -> dict:
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
        result = await db.execute(
            select(
                Key.project_id,
                func.count(Key.id).label('keys_count')
            )
            .where(Key.project_id.in_(project_ids))
            .group_by(Key.project_id)
        )
        keys_stats = result.all()
        
        # Get translations count for each project
        # Count only non-empty translations (excluding whitespace-only)
        result = await db.execute(
            select(
                Key.project_id,
                func.count(Translation.id).label('translations_count')
            )
            .join(Translation, Key.id == Translation.key_id)
            .where(
                Key.project_id.in_(project_ids),
                Translation.value.isnot(None),
                Translation.value != '',
                func.trim(Translation.value) != ''
            )
            .group_by(Key.project_id)
        )
        translations_stats = result.all()
        
        # Build result dictionary
        result_dict = {}
        
        # Add keys counts
        for project_id, keys_count in keys_stats:
            result_dict[project_id] = {'keys_count': keys_count, 'translations_count': 0}
        
        # Add translations counts
        for project_id, translations_count in translations_stats:
            if project_id in result_dict:
                result_dict[project_id]['translations_count'] = translations_count
            else:
                result_dict[project_id] = {'keys_count': 0, 'translations_count': translations_count}
        
        return result_dict

    @staticmethod
    async def get_language_progress(db: AsyncSession, project_id: int) -> dict:
        """
        Get translation progress for each language in the project.
        
        Args:
            db: Database session
            project_id: Internal project ID
            
        Returns:
            Dict mapping language code to progress percentage and counts
        """
        # Get total keys count
        result = await db.execute(
            select(func.count(Key.id)).where(Key.project_id == project_id)
        )
        keys_count = result.scalar() or 0
        
        if keys_count == 0:
            return {}
        
        # Get translations count per language
        result = await db.execute(
            select(
                Translation.language,
                func.count(Translation.id).label('translations_count')
            )
            .join(Key, Translation.key_id == Key.id)
            .where(
                Key.project_id == project_id,
                Translation.value.isnot(None),
                Translation.value != '',
                func.trim(Translation.value) != ''
            )
            .group_by(Translation.language)
        )
        language_stats = result.all()
        
        # Build result dictionary with progress percentage
        result_dict = {}
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
            
            result_dict[language] = {
                'progress': progress,
                'completed': translations_count,
                'total': keys_count
            }
        
        return result_dict

    @staticmethod
    async def get_user_projects(db: AsyncSession, user_id: int) -> List[Project]:
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
        result = await db.execute(
            select(Project)
            .options(*eager_options)
            .where(Project.owner_id == user_id)
        )
        owned_projects = result.scalars().unique().all()
        owned_project_ids = {p.id for p in owned_projects}
        
        # Get projects where user has access
        result = await db.execute(
            select(Project)
            .options(*eager_options)
            .join(ProjectAccess, Project.id == ProjectAccess.project_id)
            .where(ProjectAccess.user_id == user_id)
        )
        access_projects = result.scalars().unique().all()
        
        # Combine and deduplicate
        all_projects = list(owned_projects)
        for project in access_projects:
            if project.id not in owned_project_ids:
                all_projects.append(project)
        
        return all_projects

    @staticmethod
    async def update_project(
        db: AsyncSession,
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
        project = await ProjectService.get_project_by_public_id(db, public_id)
        if not project:
            return None
        
        # Check if user has permission to update
        if not await ProjectService.can_user_edit_project(db, project.id, user_id):
            return None
        
        # Update fields if provided and log changes
        if name is not None and name != project.name:
            old_name = project.name
            project.name = name
            await ProjectService._create_log(
                db=db,
                project_id=project.id,
                user_id=user_id,
                action=ActionType.PROJECT_UPDATE_NAME,
                field_name="name",
                old_value=old_name,
                new_value=name
            )
        
        if description is not None and description != project.description:
            old_description = project.description
            project.description = description
            await ProjectService._create_log(
                db=db,
                project_id=project.id,
                user_id=user_id,
                action=ActionType.PROJECT_UPDATE_DESCRIPTION,
                field_name="description",
                old_value=old_description or '',
                new_value=description
            )
        
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
            
            # Check if languages actually changed
            if json.dumps(languages_data, sort_keys=True) != json.dumps(project.languages, sort_keys=True):
                old_languages = project.languages
                project.languages = languages_data
                
                # Format languages as readable string for display
                old_langs_str = ', '.join([lang.get('code', '') for lang in old_languages]) if old_languages else ''
                new_langs_str = ', '.join([lang.get('code', '') for lang in languages_data])
                
                await ProjectService._create_log(
                    db=db,
                    project_id=project.id,
                    user_id=user_id,
                    action=ActionType.PROJECT_UPDATE_LANGUAGES,
                    field_name="languages",
                    old_value=old_langs_str,
                    new_value=new_langs_str,
                    extra_data={
                        'old_languages': old_languages,
                        'new_languages': languages_data
                    }
                )
        
        if default_language is not None and default_language != project.default_language:
            old_default_language = project.default_language
            project.default_language = default_language
            await ProjectService._create_log(
                db=db,
                project_id=project.id,
                user_id=user_id,
                action=ActionType.PROJECT_UPDATE_DEFAULT_LANGUAGE,
                field_name="default_language",
                old_value=old_default_language or '',
                new_value=default_language
            )
        
        if color is not None and color != project.color:
            old_color = project.color
            project.color = color
            await ProjectService._create_log(
                db=db,
                project_id=project.id,
                user_id=user_id,
                action=ActionType.PROJECT_UPDATE_COLOR,
                field_name="color",
                old_value=old_color,
                new_value=color
            )
        
        if status is not None and status != project.status:
            old_status = project.status
            project.status = status
            await ProjectService._create_log(
                db=db,
                project_id=project.id,
                user_id=user_id,
                action=ActionType.PROJECT_UPDATE_STATUS,
                field_name="status",
                old_value=old_status,
                new_value=status
            )
        
        await db.commit()
        
        # Reload with relationships
        result = await db.execute(
            select(Project)
            .options(
                joinedload(Project.owner),
                joinedload(Project.team),
                selectinload(Project.access_members).joinedload(ProjectAccess.user)
            )
            .where(Project.id == project.id)
        )
        return result.unique().scalar_one()

    @staticmethod
    async def delete_project(db: AsyncSession, public_id: str, user_id: int) -> bool:
        """
        Delete a project. Only owner can delete.
        
        Args:
            db: Database session
            public_id: Public UUID of the project
            user_id: User ID requesting the deletion
            
        Returns:
            True if deleted, False otherwise
        """
        project = await ProjectService.get_project_by_public_id(db, public_id)
        if not project:
            return False
        
        # Only owner can delete
        if project.owner_id != user_id:
            return False
        
        # Get team_id before deletion for logging
        team_id = project.team_id
        project_name = project.name
        project_id_to_delete = project.id
        
        # Delete project first (cascade will handle related records)
        await db.execute(delete(Project).where(Project.id == project_id_to_delete))
        
        # Log project deletion after delete - don't reference deleted project
        log = ActivityLog(
            team_id=team_id,
            project_id=None,  # Don't reference deleted project
            user_id=user_id,
            action=ActionType.PROJECT_DELETE,
            field_name="name",
            old_value=project_name
        )
        db.add(log)
        await db.commit()
        return True

    @staticmethod
    async def check_project_access(db: AsyncSession, project_id: int, user_id: int) -> bool:
        """
        Check if user has access to a project (owner or has ProjectAccess).
        
        Args:
            db: Database session
            project_id: Internal project ID
            user_id: User ID
            
        Returns:
            True if user has access, False otherwise
        """
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return False
        
        # Check if owner
        if project.owner_id == user_id:
            return True
        
        # Check if has project access
        result = await db.execute(
            select(ProjectAccess).where(
                ProjectAccess.project_id == project_id,
                ProjectAccess.user_id == user_id
            )
        )
        access = result.scalar_one_or_none()
        
        return access is not None

    @staticmethod
    async def can_user_edit_project(db: AsyncSession, project_id: int, user_id: int) -> bool:
        """
        Check if user can edit a project (owner or admin access).
        
        Args:
            db: Database session
            project_id: Internal project ID
            user_id: User ID
            
        Returns:
            True if user can edit, False otherwise
        """
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return False
        
        # Owner can always edit
        if project.owner_id == user_id:
            return True
        
        # Check if has admin access
        result = await db.execute(
            select(ProjectAccess).where(
                ProjectAccess.project_id == project_id,
                ProjectAccess.user_id == user_id,
                ProjectAccess.role == "admin"
            )
        )
        access = result.scalar_one_or_none()
        
        return access is not None

    @staticmethod
    async def add_project_member(
        db: AsyncSession,
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
        project = await ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return None
        
        # Check permission
        if not await ProjectService.can_user_edit_project(db, project.id, added_by_user_id):
            return None
        
        # Get user to add
        try:
            uuid_obj = uuid_lib.UUID(user_public_id)
            result = await db.execute(select(User).where(User.public_id == uuid_obj))
            user = result.scalar_one_or_none()
            if not user:
                return None
        except (ValueError, AttributeError):
            return None
        
        # Check if already a member
        result = await db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project.id,
                ProjectMember.user_id == user.id
            )
        )
        existing_member = result.scalar_one_or_none()
        
        if existing_member:
            # Update role if already exists
            existing_member.role = role
            await db.commit()
            await db.refresh(existing_member)
            return existing_member
        
        # Create new member
        member = ProjectMember(
            project_id=project.id,
            user_id=user.id,
            role=role
        )
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member

    @staticmethod
    async def remove_project_member(
        db: AsyncSession,
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
        project = await ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return False
        
        # Check permission
        if not await ProjectService.can_user_edit_project(db, project.id, removed_by_user_id):
            return False
        
        # Get user to remove
        try:
            uuid_obj = uuid_lib.UUID(user_public_id)
            result = await db.execute(select(User).where(User.public_id == uuid_obj))
            user = result.scalar_one_or_none()
            if not user:
                return False
        except (ValueError, AttributeError):
            return False
        
        # Cannot remove owner
        if project.owner_id == user.id:
            return False
        
        # Find and remove project access
        result = await db.execute(
            select(ProjectAccess).where(
                ProjectAccess.project_id == project.id,
                ProjectAccess.user_id == user.id
            )
        )
        access = result.scalar_one_or_none()
        
        if not access:
            return False
        
        db.delete(access)
        await db.commit()
        return True

    @staticmethod
    async def transfer_project(
        db: AsyncSession,
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
        project = await ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return None
        
        # Only owner can transfer
        if project.owner_id != user_id:
            return None
        
        # Verify new team exists and user has access to it
        result = await db.execute(select(Team).where(Team.id == new_team_id))
        team = result.scalar_one_or_none()
        if not team:
            return None
        
        # Verify user is owner or member of new team
        from app.services.team_service import TeamService
        if not await TeamService.check_user_team_access(db, new_team_id, user_id):
            return None
        
        # Remove all existing project access entries
        await db.execute(
            delete(ProjectAccess).where(ProjectAccess.project_id == project.id)
        )
        
        # Update project team
        project.team_id = new_team_id
        await db.commit()
        await db.refresh(project)
        
        return project

    @staticmethod
    async def export_project_data(db: AsyncSession, project_public_id: str, user_id: int) -> Optional[dict]:
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
        project = await ProjectService.get_project_by_public_id(db, project_public_id)
        if not project:
            return None
        
        # Check access
        if not await ProjectService.check_project_access(db, project.id, user_id):
            return None
        
        # Log export action
        await ProjectService._create_log(
            db=db,
            project_id=project.id,
            user_id=user_id,
            action=ActionType.PROJECT_EXPORT,
            field_name="export"
        )
        await db.commit()
        
        # Get all keys with translations
        result = await db.execute(select(Key).where(Key.project_id == project.id))
        keys = result.scalars().all()
        
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
                result = await db.execute(
                    select(Translation).where(
                        Translation.key_id == key.id,
                        Translation.language == code
                    )
                )
                translation = result.scalar_one_or_none()
                
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
    async def import_project_data(
        db: AsyncSession,
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
            project = await ProjectService.create_project(
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
            
            # Log project import (ActivityLog already imported at top of file)
            # Note: ActivityLog is already imported at module level
            await ProjectService._create_log(
                db=db,
                project_id=project.id,
                user_id=owner_id,
                action=ActionType.PROJECT_IMPORT,
                field_name="import",
                extra_data={
                    'keys_count': len(keys_data),
                    'locales_count': len(locales)
                }
            )
            
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
                await db.flush()
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
                        result = await db.execute(
                            select(Key).where(
                                Key.project_id == project.id,
                                Key.key == key_str
                            )
                        )
                        key_obj = result.scalar_one_or_none()
                        
                        if not key_obj:
                            key_obj = Key(
                                key=key_str,
                                project_id=project.id
                            )
                            db.add(key_obj)
                            await db.flush()
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
            await db.commit()
            await db.refresh(project)
            logger.info(f"Import completed successfully for project: {project.public_id}")
            return project
            
        except Exception as e:
            logger.error(f"Import failed with error: {type(e).__name__}: {str(e)}")
            logger.exception("Full traceback:")
            await db.rollback()
            raise e
