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

from app.database import AsyncSessionLocal
from app.models.scan_session import ScanSession, ScanStatus, AIProvider
from app.models.found_string import FoundString, FoundStringStatus
from app.models.repository import Repository
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
    created_at: datetime


@strawberry.type
class ScanSessionType:
    """GraphQL type for scan session."""
    id: str  # Public UUID
    status: ScanStatusEnum
    ai_provider: AIProviderEnum
    ai_model: str
    files_total: int
    files_scanned: int
    strings_found: int
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    found_strings: List[FoundStringType]


@strawberry.type
class TokenUsageStatsType:
    """GraphQL type for token usage statistics."""
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    operations_count: int


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


def _session_to_type(session: ScanSession, found_strings: List[FoundString] = None) -> ScanSessionType:
    """Convert ScanSession model to GraphQL type."""
    strings_list = []
    if found_strings:
        for fs in found_strings:
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
                created_at=fs.created_at,
            ))
    
    return ScanSessionType(
        id=str(session.public_id),
        status=ScanStatusEnum(session.status.value),
        ai_provider=AIProviderEnum(session.ai_provider.value),
        ai_model=session.ai_model,
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
                    )
                
                has_access = await TeamService.check_user_team_access(db, team.id, user_id)
                if not has_access and team.owner_id != user_id:
                    return TokenUsageStatsType(
                        total_input_tokens=0,
                        total_output_tokens=0,
                        total_tokens=0,
                        operations_count=0,
                    )
                
                stats = await TokenUsageService.get_team_usage(db, team.id, days)
                
                return TokenUsageStatsType(
                    total_input_tokens=stats["total_input_tokens"],
                    total_output_tokens=stats["total_output_tokens"],
                    total_tokens=stats["total_tokens"],
                    operations_count=stats["operations_count"],
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
            )


@strawberry.type
class ScannerMutation:
    """GraphQL mutations for scanner."""
    
    @strawberry.mutation
    async def start_repository_scan(
        self,
        info: Info,
        project_id: str,
        ai_provider: Optional[str] = None,
        ai_model: Optional[str] = None,
    ) -> StartScanResult:
        """
        Start scanning a repository for hardcoded strings.
        
        Args:
            info: GraphQL info object
            project_id: Public UUID of the project
            ai_provider: Optional AI provider (OPENAI or ANTHROPIC)
            ai_model: Optional specific model to use
            
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
                
                # Create scan session
                session = await ScannerService.start_scan(
                    db=db,
                    repository_id=repository.id,
                    user_id=user_id,
                    ai_provider=ai_provider,
                    ai_model=ai_model,
                )
                
                # Start background processing
                # Note: In production, you'd use Celery or similar task queue
                # For now, we use asyncio.create_task
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

