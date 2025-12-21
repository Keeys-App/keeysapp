"""
GraphQL schema for repository scanning.
"""
import strawberry
from typing import Optional, List
from datetime import datetime
from strawberry.types import Info
from enum import Enum
import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database import AsyncSessionLocal
from app.models.scan_session import ScanSession
from app.models.found_string import FoundString, FoundStringStatus
from app.models.repository import Repository
from app.models.github_connection import GitHubConnection
from app.models.activity_log import ActivityLog, ActionType
from app.models.key import Key, Translation
from app.models.project import Project
from app.services.scanner_service import ScannerService
from app.services.token_usage_service import TokenUsageService
from app.services.github_service import GitHubService
from app.services.project_service import ProjectService
from app.services.team_service import TeamService
from app.schemas.github import get_current_user_id
from app.core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


@strawberry.enum
class ScanStatusEnum(str, Enum):
    """GraphQL enum for scan status."""
    PENDING = "PENDING"
    SCANNING = "SCANNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@strawberry.enum
class AIProviderEnum(str, Enum):
    """GraphQL enum for AI provider."""
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"


@strawberry.enum
class FoundStringStatusEnum(str, Enum):
    """GraphQL enum for found string status."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    SKIPPED = "SKIPPED"
    CONVERTED = "CONVERTED"
    MATCHED = "MATCHED"


@strawberry.type
class FoundStringType:
    """GraphQL type for found string."""
    id: str  # Public UUID
    file_path: str
    line_number: Optional[int]
    original_text: str
    suggested_key: str
    context: Optional[str]
    confidence: int  # 0-100
    status: FoundStringStatusEnum
    key_id: Optional[str]  # Public UUID of linked key
    matched_key_id: Optional[str]  # Public UUID of matched existing key
    matched_key_name: Optional[str]  # Name of matched existing key
    file_type: Optional[str]  # File extension (e.g., "tsx", "vue", "py")
    file_language: Optional[str]  # Programming language (e.g., "TypeScript", "Python")
    file_framework: Optional[str]  # Framework (e.g., "React", "Vue", "Svelte")
    created_at: datetime


@strawberry.type
class ScanSessionType:
    """GraphQL type for scan session."""
    id: str  # Public UUID
    status: ScanStatusEnum
    ai_provider: AIProviderEnum
    ai_model: str
    scan_path: Optional[str]  # Directory to scan (None = entire repo)
    files_total: int
    files_scanned: int
    strings_found: int
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    found_strings: List[FoundStringType]


@strawberry.type
class RepositoryDirectoryType:
    """GraphQL type for repository directory."""
    path: str
    name: str
    is_recommended: bool = False  # True for directories likely containing localizable content


# Directories to always ignore (not useful for localization scanning)
IGNORED_DIRECTORIES = {
    'node_modules',
    '.git',
    '.github',
    '.vscode',
    '.idea',
    'dist',
    'build',
    'out',
    '.next',
    '.nuxt',
    '.output',
    '.yarn',
    '.pnpm',
    'vendor',
    '__pycache__',
    '.pytest_cache',
    'venv',
    '.venv',
    'env',
    '.env',
    'coverage',
    '.coverage',
    '.nyc_output',
    'tmp',
    'temp',
    'logs',
    'cache',
    '.cache',
    'public',  # Usually static assets, not code
    'static',  # Usually static assets
    'assets',  # Usually images/fonts
    'migrations',  # Database migrations
    'alembic',  # Database migrations (Python)
    'tests',  # Test files
    'test',
    '__tests__',
    'spec',
    'specs',
}

# Directory names that are top-level project directories (highest priority)
TOP_LEVEL_DIRECTORIES = {
    'frontend',
    'client',
    'web',
    'backend',
    'server',
    'api',
}

# Directory names that likely contain localizable code (high priority)
RECOMMENDED_DIRECTORIES = {
    'src',
    'app',
    'pages',
    'components',
    'views',
    'screens',
    'features',
    'modules',
    'ui',
    'lib',  # Often contains shared code
}


def get_directory_priority(path: str, name: str) -> tuple:
    """
    Get sorting priority for a directory based on full path.
    Returns tuple for multi-level sorting. Lower = higher priority (shown first).
    """
    path_lower = path.lower()
    name_lower = name.lower()
    path_parts = path_lower.split('/')
    depth = len(path_parts)
    
    # Check if path starts with a top-level directory (frontend, backend, etc.)
    is_top_level_root = path_parts[0] in TOP_LEVEL_DIRECTORIES if path_parts else False
    
    if is_top_level_root:
        # frontend, backend, frontend/src - highest priority, sorted by depth
        return (0, depth, path)
    
    if name_lower in TOP_LEVEL_DIRECTORIES:
        # Directory named frontend/backend but nested somewhere
        return (1, depth, path)
    
    if name_lower in RECOMMENDED_DIRECTORIES:
        # Recommended directories like src, components
        return (2, depth, path)
    
    # Everything else
    return (3, depth, path)


@strawberry.type
class TokenUsageBreakdownItem:
    """GraphQL type for token usage breakdown by category."""
    name: str
    tokens: int


@strawberry.type
class TokenUsageStatsType:
    """GraphQL type for token usage statistics."""
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    operations_count: int
    by_operation: List[TokenUsageBreakdownItem]
    by_provider: List[TokenUsageBreakdownItem]
    by_model: List[TokenUsageBreakdownItem]


@strawberry.type
class StartScanResult:
    """Result type for starting a scan."""
    success: bool
    message: str
    scan_session: Optional[ScanSessionType] = None


@strawberry.type
class UpdateFoundStringResult:
    """Result type for updating found string status."""
    success: bool
    message: str
    found_string: Optional[FoundStringType] = None


@strawberry.type
class ConvertStringsResult:
    """Result type for converting found strings to keys."""
    success: bool
    message: str
    keys_created: int


@strawberry.type
class ReplaceFoundStringResult:
    """Result type for replacing an existing key with found string."""
    success: bool
    message: str
    found_string: Optional[FoundStringType] = None


def _session_to_type(session: ScanSession, found_strings: List[FoundString] = None) -> ScanSessionType:
    """Convert ScanSession model to GraphQL type."""
    strings_list = []
    if found_strings:
        for fs in found_strings:
            # Get matched key info if available
            matched_key_public_id = None
            matched_key_name = None
            if fs.matched_key_id and hasattr(fs, 'matched_key') and fs.matched_key:
                matched_key_public_id = str(fs.matched_key.public_id)
                matched_key_name = fs.matched_key.key
            
            strings_list.append(FoundStringType(
                id=str(fs.public_id),
                file_path=fs.file_path,
                line_number=fs.line_number,
                original_text=fs.original_text,
                suggested_key=fs.suggested_key,
                context=fs.context,
                confidence=fs.confidence,
                status=FoundStringStatusEnum(fs.status.value),
                key_id=str(fs.key.public_id) if fs.key_id and hasattr(fs, 'key') and fs.key else None,
                matched_key_id=matched_key_public_id,
                matched_key_name=matched_key_name,
                file_type=fs.file_type,
                file_language=fs.file_language,
                file_framework=fs.file_framework,
                created_at=fs.created_at,
            ))
    
    return ScanSessionType(
        id=str(session.public_id),
        status=ScanStatusEnum(session.status.value),
        ai_provider=AIProviderEnum(session.ai_provider.value),
        ai_model=session.ai_model,
        scan_path=session.scan_path,
        files_total=session.files_total,
        files_scanned=session.files_scanned,
        strings_found=session.strings_found,
        error_message=session.error_message,
        created_at=session.created_at,
        started_at=session.started_at,
        completed_at=session.completed_at,
        found_strings=strings_list,
    )


@strawberry.type
class ScannerQuery:
    """GraphQL queries for scanner."""
    
    @strawberry.field
    async def scan_session(
        self,
        info: Info,
        scan_session_id: str,
    ) -> Optional[ScanSessionType]:
        """
        Get a scan session by ID with its found strings.
        
        Args:
            info: GraphQL info object
            scan_session_id: Public UUID of the scan session
            
        Returns:
            Scan session with found strings or None
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                session = await ScannerService.get_scan_session(db, scan_session_id)
                
                if not session:
                    return None
                
                # Note: Stale scan detection is handled by resume_interrupted_scans on server startup
                # We don't auto-fail scans during queries because long scans are normal
                
                # Get repository to check access (use repository_id, not lazy relationship)
                result = await db.execute(
                    select(Repository).where(Repository.id == session.repository_id)
                )
                repository = result.scalar_one_or_none()
                if not repository:
                    return None
                
                # Check project access
                has_access = await ProjectService.check_project_access(db, repository.project_id, user_id)
                if not has_access:
                    return None
                
                # Get found strings
                found_strings = await ScannerService.get_found_strings(db, session.id)
                
                return _session_to_type(session, found_strings)
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error fetching scan session: {type(e).__name__}: {str(e)}")
            return None
    
    @strawberry.field
    async def project_scan_sessions(
        self,
        info: Info,
        project_id: str,
        limit: int = 10,
    ) -> List[ScanSessionType]:
        """
        Get scan sessions for a project.
        
        Args:
            info: GraphQL info object
            project_id: Public UUID of the project
            limit: Maximum number of sessions to return
            
        Returns:
            List of scan sessions
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                # Get project and check access
                project = await ProjectService.get_project_by_public_id(db, project_id)
                if not project:
                    return []
                
                has_access = await ProjectService.check_project_access(db, project.id, user_id)
                if not has_access:
                    return []
                
                # Get repository
                repository = await GitHubService.get_repository_by_project(db, project.id)
                if not repository:
                    return []
                
                # Get scan sessions
                sessions = await ScannerService.get_scan_sessions_by_repository(db, repository.id, limit)
                
                return [_session_to_type(s) for s in sessions]
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error fetching scan sessions: {type(e).__name__}: {str(e)}")
            return []
    
    @strawberry.field
    async def team_token_usage(
        self,
        info: Info,
        team_id: str,
        days: int = 30,
    ) -> TokenUsageStatsType:
        """
        Get token usage statistics for a team.
        
        Args:
            info: GraphQL info object
            team_id: Public UUID of the team
            days: Number of days to look back
            
        Returns:
            Token usage statistics
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                # Get team and check access
                team = await TeamService.get_team_by_public_id(db, team_id)
                if not team:
                    return TokenUsageStatsType(
                        total_input_tokens=0,
                        total_output_tokens=0,
                        total_tokens=0,
                        operations_count=0,
                        by_operation=[],
                        by_provider=[],
                        by_model=[],
                    )
                
                has_access = await TeamService.check_user_team_access(db, team.id, user_id)
                if not has_access and team.owner_id != user_id:
                    return TokenUsageStatsType(
                        total_input_tokens=0,
                        total_output_tokens=0,
                        total_tokens=0,
                        operations_count=0,
                        by_operation=[],
                        by_provider=[],
                        by_model=[],
                    )
                
                stats = await TokenUsageService.get_team_usage(db, team.id, days)
                
                return TokenUsageStatsType(
                    total_input_tokens=stats["total_input_tokens"],
                    total_output_tokens=stats["total_output_tokens"],
                    total_tokens=stats["total_tokens"],
                    operations_count=stats["operations_count"],
                    by_operation=[
                        TokenUsageBreakdownItem(name=k, tokens=v) 
                        for k, v in stats["by_operation"].items()
                    ],
                    by_provider=[
                        TokenUsageBreakdownItem(name=k, tokens=v) 
                        for k, v in stats["by_provider"].items()
                    ],
                    by_model=[
                        TokenUsageBreakdownItem(name=k, tokens=v) 
                        for k, v in stats["by_model"].items()
                    ],
                )
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error fetching token usage: {type(e).__name__}: {str(e)}")
            return TokenUsageStatsType(
                total_input_tokens=0,
                total_output_tokens=0,
                total_tokens=0,
                operations_count=0,
                by_operation=[],
                by_provider=[],
                by_model=[],
            )
    
    @strawberry.field
    async def repository_directories(
        self,
        info: Info,
        project_id: str,
        prefix: Optional[str] = None,
    ) -> List[RepositoryDirectoryType]:
        """
        Get list of directories from a repository.
        Used for directory picker with autocomplete.
        
        Args:
            info: GraphQL info object
            project_id: Public UUID of the project
            prefix: Optional prefix to filter directories
            
        Returns:
            List of directories matching prefix
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                # Get project and check access
                project = await ProjectService.get_project_by_public_id(db, project_id)
                if not project:
                    return []
                
                has_access = await ProjectService.check_project_access(db, project.id, user_id)
                if not has_access:
                    return []
                
                # Get repository
                repository = await GitHubService.get_repository_by_project(db, project.id)
                if not repository:
                    return []
                
                # Get GitHub connection
                result = await db.execute(
                    select(GitHubConnection).where(
                        GitHubConnection.id == repository.github_connection_id
                    )
                )
                connection = result.scalar_one_or_none()
                if not connection:
                    return []
                
                # Get access token (with auto-refresh)
                access_token = await GitHubService.get_valid_access_token(db, connection)
                if not access_token:
                    logger.warning(f"Token expired and refresh failed for connection {connection.id}")
                    return []
                
                # Get repository tree
                tree = await GitHubService.get_repository_tree(
                    access_token=access_token,
                    owner=repository.repo_owner,
                    repo=repository.repo_name,
                    branch=repository.default_branch or "main",
                )
                
                if not tree:
                    return []
                
                # Filter directories only
                directories: List[RepositoryDirectoryType] = []
                seen_paths = set()
                
                for entry in tree:
                    if entry.get("type") == "tree":  # tree = directory in GitHub API
                        path = entry.get("path", "")
                        if path and path not in seen_paths:
                            # Get directory name (last part of path)
                            name = path.split("/")[-1] if "/" in path else path
                            
                            # Skip ignored directories (check each path segment)
                            path_parts = path.lower().split("/")
                            if any(part in IGNORED_DIRECTORIES for part in path_parts):
                                continue
                            
                            # Filter by prefix if provided
                            if prefix:
                                # Match if path starts with prefix or contains prefix
                                prefix_lower = prefix.lower()
                                if not (path.lower().startswith(prefix_lower) or 
                                       prefix_lower in path.lower()):
                                    continue
                            
                            seen_paths.add(path)
                            
                            # Check if this directory is recommended for localization
                            name_lower = name.lower()
                            path_lower = path.lower()
                            path_parts = path_lower.split('/')
                            depth = len(path_parts)
                            
                            # Only recommend directories at depth 1-2 (e.g., frontend, frontend/src)
                            # Deeper directories (frontend/src/components) should not be highlighted
                            is_shallow = depth <= 2
                            
                            # Recommended if: shallow + top-level or recommended directory
                            is_top_level = name_lower in TOP_LEVEL_DIRECTORIES or path_parts[0] in TOP_LEVEL_DIRECTORIES
                            is_recommended_name = name_lower in RECOMMENDED_DIRECTORIES
                            
                            is_recommended = is_shallow and (is_top_level or is_recommended_name)
                            
                            directories.append(RepositoryDirectoryType(
                                path=path,
                                name=name,
                                is_recommended=is_recommended,
                            ))
                
                # Sort: by priority (frontend paths first, then recommended, then others)
                directories.sort(key=lambda d: get_directory_priority(d.path, d.name))
                
                # Limit results to prevent huge responses
                return directories[:100]
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error fetching repository directories: {type(e).__name__}: {str(e)}")
            return []


@strawberry.type
class ScannerMutation:
    """GraphQL mutations for scanner."""
    
    @strawberry.mutation
    async def start_repository_scan(
        self,
        info: Info,
        project_id: str,
        scan_path: Optional[str] = None,
    ) -> StartScanResult:
        """
        Start scanning a repository for hardcoded strings.
        AI settings are taken from the Team configuration.
        
        Args:
            info: GraphQL info object
            project_id: Public UUID of the project
            scan_path: Optional directory path to limit scan scope
            
        Returns:
            Result with scan session info
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                # Get project and check access
                project = await ProjectService.get_project_by_public_id(db, project_id)
                if not project:
                    return StartScanResult(
                        success=False,
                        message="Project not found",
                    )
                
                has_access = await ProjectService.check_project_access(db, project.id, user_id)
                if not has_access:
                    return StartScanResult(
                        success=False,
                        message="Access denied",
                    )
                
                # Get repository
                repository = await GitHubService.get_repository_by_project(db, project.id)
                if not repository:
                    return StartScanResult(
                        success=False,
                        message="No repository connected to this project",
                    )
                
                # Get AI settings from Team (NEVER from frontend!)
                team = await TeamService.get_team_by_id(db, project.team_id)
                if not team:
                    return StartScanResult(
                        success=False,
                        message="Team not found",
                    )
                
                ai_provider = team.ai_provider
                ai_model = team.ai_model
                
                # Validate scan_path if provided
                if scan_path:
                    # Normalize path (remove leading/trailing slashes)
                    scan_path = scan_path.strip("/")
                    
                    if scan_path:
                        # Get GitHub connection
                        conn_result = await db.execute(
                            select(GitHubConnection).where(
                                GitHubConnection.id == repository.github_connection_id
                            )
                        )
                        connection = conn_result.scalar_one_or_none()
                        if not connection:
                            return StartScanResult(
                                success=False,
                                message="GitHub connection not found",
                            )
                        
                        # Verify directory exists (with auto-refresh)
                        access_token = await GitHubService.get_valid_access_token(db, connection)
                        if not access_token:
                            return StartScanResult(
                                success=False,
                                message="GitHub token expired. Please reconnect your account.",
                            )
                        tree = await GitHubService.get_repository_tree(
                            access_token=access_token,
                            owner=repository.repo_owner,
                            repo=repository.repo_name,
                            branch=repository.default_branch or "main",
                        )
                        
                        if tree:
                            # Check if directory exists in tree
                            dir_exists = any(
                                entry.get("type") == "tree" and entry.get("path") == scan_path
                                for entry in tree
                            )
                            if not dir_exists:
                                return StartScanResult(
                                    success=False,
                                    message=f"Directory '{scan_path}' not found in repository",
                                )
                    else:
                        # Empty after strip means scan entire repo
                        scan_path = None
                
                # Create scan session
                session = await ScannerService.start_scan(
                    db=db,
                    repository_id=repository.id,
                    user_id=user_id,
                    ai_provider=ai_provider,
                    ai_model=ai_model,
                    scan_path=scan_path,
                )
                
                # Log scan start activity
                scan_start_log = ActivityLog(
                    team_id=project.team_id,
                    project_id=project.id,
                    user_id=user_id,
                    action=ActionType.SCAN_START,
                    extra_data={
                        "repository": repository.full_name,
                        "ai_provider": ai_provider,
                        "ai_model": ai_model,
                        "scan_session_id": str(session.public_id),
                        "scan_path": scan_path,
                    }
                )
                db.add(scan_start_log)
                await db.commit()
                
                # Start background processing
                team_id = project.team_id
                
                async def run_scan():
                    async with AsyncSessionLocal() as scan_db:
                        await ScannerService.process_scan(scan_db, session.id, team_id)
                
                asyncio.create_task(run_scan())
                
                return StartScanResult(
                    success=True,
                    message="Scan started",
                    scan_session=_session_to_type(session),
                )
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error starting scan: {type(e).__name__}: {str(e)}")
            return StartScanResult(
                success=False,
                message="Failed to start scan. Please try again.",
            )
    
    @strawberry.mutation
    async def cancel_scan(
        self,
        info: Info,
        scan_session_id: str,
    ) -> StartScanResult:
        """
        Cancel a running scan.
        
        Args:
            info: GraphQL info object
            scan_session_id: Public UUID of the scan session
            
        Returns:
            Result with success status
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                session = await ScannerService.get_scan_session(db, scan_session_id)
                
                if not session:
                    return StartScanResult(
                        success=False,
                        message="Scan session not found",
                    )
                
                # Check access through repository -> project (use repository_id, not lazy relationship)
                result = await db.execute(
                    select(Repository).where(Repository.id == session.repository_id)
                )
                repository = result.scalar_one_or_none()
                if repository:
                    has_access = await ProjectService.check_project_access(db, repository.project_id, user_id)
                    if not has_access:
                        return StartScanResult(
                            success=False,
                            message="Access denied",
                        )
                
                cancelled = await ScannerService.cancel_scan(db, session.id)
                
                if cancelled:
                    await db.refresh(session)
                    
                    # Log scan cancelled activity
                    if repository:
                        from app.models.project import Project
                        proj_result = await db.execute(
                            select(Project).where(Project.id == repository.project_id)
                        )
                        project = proj_result.scalar_one_or_none()
                        if project:
                            scan_cancelled_log = ActivityLog(
                                team_id=project.team_id,
                                project_id=project.id,
                                user_id=user_id,
                                action=ActionType.SCAN_CANCELLED,
                                extra_data={
                                    "repository": repository.full_name,
                                    "scan_session_id": str(session.public_id),
                                }
                            )
                            db.add(scan_cancelled_log)
                            await db.commit()
                    
                    return StartScanResult(
                        success=True,
                        message="Scan cancelled",
                        scan_session=_session_to_type(session),
                    )
                else:
                    return StartScanResult(
                        success=False,
                        message="Cannot cancel scan (already completed or failed)",
                    )
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error cancelling scan: {type(e).__name__}: {str(e)}")
            return StartScanResult(
                success=False,
                message="Failed to cancel scan. Please try again.",
            )
    
    @strawberry.mutation
    async def update_found_string_status(
        self,
        info: Info,
        found_string_id: str,
        status: FoundStringStatusEnum,
    ) -> UpdateFoundStringResult:
        """
        Update the status of a found string (approve/skip).
        
        Args:
            info: GraphQL info object
            found_string_id: Public UUID of the found string
            status: New status (APPROVED or SKIPPED)
            
        Returns:
            Result with updated found string
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                from uuid import UUID
                
                # Get found string
                try:
                    uuid_obj = UUID(found_string_id)
                    result = await db.execute(
                        select(FoundString).where(FoundString.public_id == uuid_obj)
                    )
                    found_string = result.scalar_one_or_none()
                except (ValueError, AttributeError):
                    found_string = None
                
                if not found_string:
                    return UpdateFoundStringResult(
                        success=False,
                        message="Found string not found",
                    )
                
                # Get scan session to check access
                result = await db.execute(
                    select(ScanSession).where(ScanSession.id == found_string.scan_session_id)
                )
                session = result.scalar_one_or_none()
                
                if not session:
                    return UpdateFoundStringResult(
                        success=False,
                        message="Scan session not found",
                    )
                
                # Check access through repository -> project
                result = await db.execute(
                    select(Repository).where(Repository.id == session.repository_id)
                )
                repository = result.scalar_one_or_none()
                
                if repository:
                    has_access = await ProjectService.check_project_access(db, repository.project_id, user_id)
                    if not has_access:
                        return UpdateFoundStringResult(
                            success=False,
                            message="Access denied",
                        )
                
                # Update status
                new_status = FoundStringStatus(status.value)
                updated = await ScannerService.update_found_string_status(db, found_string.id, new_status)
                
                if updated:
                    return UpdateFoundStringResult(
                        success=True,
                        message="Status updated",
                        found_string=FoundStringType(
                            id=str(updated.public_id),
                            file_path=updated.file_path,
                            line_number=updated.line_number,
                            original_text=updated.original_text,
                            suggested_key=updated.suggested_key,
                            context=updated.context,
                            confidence=updated.confidence,
                            status=FoundStringStatusEnum(updated.status.value),
                            key_id=None,
                            matched_key_id=None,
                            matched_key_name=None,
                            file_type=updated.file_type,
                            file_language=updated.file_language,
                            file_framework=updated.file_framework,
                            created_at=updated.created_at,
                        ),
                    )
                else:
                    return UpdateFoundStringResult(
                        success=False,
                        message="Failed to update status",
                    )
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error updating found string: {type(e).__name__}: {str(e)}")
            return UpdateFoundStringResult(
                success=False,
                message="Failed to update status. Please try again.",
            )
    
    @strawberry.mutation
    async def convert_found_strings_to_keys(
        self,
        info: Info,
        scan_session_id: str,
    ) -> ConvertStringsResult:
        """
        Convert all approved found strings to translation keys.
        
        Args:
            info: GraphQL info object
            scan_session_id: Public UUID of the scan session
            
        Returns:
            Result with number of keys created
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                session = await ScannerService.get_scan_session(db, scan_session_id)
                
                if not session:
                    return ConvertStringsResult(
                        success=False,
                        message="Scan session not found",
                        keys_created=0,
                    )
                
                # Get repository and project
                result = await db.execute(
                    select(Repository).where(Repository.id == session.repository_id)
                )
                repository = result.scalar_one_or_none()
                
                if not repository:
                    return ConvertStringsResult(
                        success=False,
                        message="Repository not found",
                        keys_created=0,
                    )
                
                # Check access
                has_access = await ProjectService.check_project_access(db, repository.project_id, user_id)
                if not has_access:
                    return ConvertStringsResult(
                        success=False,
                        message="Access denied",
                        keys_created=0,
                    )
                
                # Get project for default language
                from app.models.project import Project
                result = await db.execute(
                    select(Project).where(Project.id == repository.project_id)
                )
                project = result.scalar_one_or_none()
                default_language = project.default_language or "en" if project else "en"
                
                # Convert strings
                keys_created = await ScannerService.convert_found_strings_to_keys(
                    db=db,
                    scan_session_id=session.id,
                    project_id=repository.project_id,
                    default_language=default_language,
                )
                
                return ConvertStringsResult(
                    success=True,
                    message=f"Created {keys_created} keys",
                    keys_created=keys_created,
                )
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error converting strings: {type(e).__name__}: {str(e)}")
            return ConvertStringsResult(
                success=False,
                message="Failed to convert strings. Please try again.",
                keys_created=0,
            )
    
    @strawberry.mutation
    async def replace_found_string(
        self,
        info: Info,
        found_string_id: str,
    ) -> ReplaceFoundStringResult:
        """
        Replace an existing key's default translation with the found string's text.
        Also updates the key's source file metadata.
        
        This mutation is used for MATCHED found strings where we want to update
        the existing key instead of creating a new one.
        
        Args:
            info: GraphQL info object
            found_string_id: Public UUID of the found string
            
        Returns:
            Result with updated found string
        """
        try:
            user_id = await get_current_user_id(info)
            
            async with AsyncSessionLocal() as db:
                # Get found string with matched key
                result = await db.execute(
                    select(FoundString)
                    .options(joinedload(FoundString.matched_key))
                    .where(FoundString.public_id == found_string_id)
                )
                found_string = result.scalar_one_or_none()
                
                if not found_string:
                    return ReplaceFoundStringResult(
                        success=False,
                        message="Found string not found",
                    )
                
                # Check if it has a matched key
                if not found_string.matched_key_id:
                    return ReplaceFoundStringResult(
                        success=False,
                        message="No matched key to replace",
                    )
                
                # Get scan session to verify access
                session = await ScannerService.get_scan_session_by_id(db, found_string.scan_session_id)
                if not session:
                    return ReplaceFoundStringResult(
                        success=False,
                        message="Scan session not found",
                    )
                
                # Get repository and check access
                repo_result = await db.execute(
                    select(Repository).where(Repository.id == session.repository_id)
                )
                repository = repo_result.scalar_one_or_none()
                
                if not repository:
                    return ReplaceFoundStringResult(
                        success=False,
                        message="Repository not found",
                    )
                
                has_access = await ProjectService.check_project_access(db, repository.project_id, user_id)
                if not has_access:
                    return ReplaceFoundStringResult(
                        success=False,
                        message="Access denied",
                    )
                
                # Get the matched key
                key_result = await db.execute(
                    select(Key).where(Key.id == found_string.matched_key_id)
                )
                matched_key = key_result.scalar_one_or_none()
                
                if not matched_key:
                    return ReplaceFoundStringResult(
                        success=False,
                        message="Matched key not found",
                    )
                
                # Get project default language
                proj_result = await db.execute(
                    select(Project).where(Project.id == repository.project_id)
                )
                project = proj_result.scalar_one_or_none()
                default_language = project.default_language or "en" if project else "en"
                
                # Update or create translation for default language
                trans_result = await db.execute(
                    select(Translation).where(
                        Translation.key_id == matched_key.id,
                        Translation.language == default_language,
                    )
                )
                translation = trans_result.scalar_one_or_none()
                
                if translation:
                    translation.value = found_string.original_text
                else:
                    translation = Translation(
                        key_id=matched_key.id,
                        language=default_language,
                        value=found_string.original_text,
                    )
                    db.add(translation)
                
                # Update key's source file metadata
                matched_key.source_file_path = found_string.file_path
                matched_key.source_line_number = found_string.line_number
                
                # Update found string status to APPROVED
                found_string.status = FoundStringStatus.APPROVED
                
                await db.commit()
                
                return ReplaceFoundStringResult(
                    success=True,
                    message="Key translation replaced successfully",
                    found_string=FoundStringType(
                        id=str(found_string.public_id),
                        file_path=found_string.file_path,
                        line_number=found_string.line_number,
                        original_text=found_string.original_text,
                        suggested_key=found_string.suggested_key,
                        context=found_string.context,
                        confidence=found_string.confidence,
                        status=FoundStringStatusEnum(found_string.status.value),
                        key_id=None,
                        matched_key_id=str(matched_key.public_id),
                        matched_key_name=matched_key.key,
                        file_type=found_string.file_type,
                        file_language=found_string.file_language,
                        file_framework=found_string.file_framework,
                        created_at=found_string.created_at,
                    ),
                )
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error replacing found string: {type(e).__name__}: {str(e)}")
            return ReplaceFoundStringResult(
                success=False,
                message="Failed to replace key. Please try again.",
            )

