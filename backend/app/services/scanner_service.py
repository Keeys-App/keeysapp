"""
Scanner Service for repository code analysis.
Handles the scanning of repositories to find hardcoded strings.
Uses arq (Redis queue) for background processing.
"""
import asyncio
import logging
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from arq import create_pool
from arq.connections import RedisSettings

from app.models.scan_session import ScanSession, ScanStatus, AIProvider
from app.models.found_string import FoundString, FoundStringStatus
from app.models.repository import Repository
from app.models.github_connection import GitHubConnection
from app.models.key import Key, Translation
from app.models.user import User
from app.models.project import Project
from app.models.activity_log import ActivityLog, ActionType
from app.services.github_service import GitHubService
from app.services.token_usage_service import TokenUsageService
from app.services.email_service import send_scan_completed_email_background
from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_redis_settings() -> RedisSettings:
    """Parse Redis URL and return RedisSettings."""
    url = settings.redis_url
    
    # Parse redis://host:port or redis://user:pass@host:port/db
    if url.startswith("redis://"):
        url = url[8:]
    
    # Handle authentication
    if "@" in url:
        auth, host_part = url.rsplit("@", 1)
        if ":" in auth:
            password = auth.split(":", 1)[1]
        else:
            password = None
    else:
        host_part = url
        password = None
    
    # Handle database number
    if "/" in host_part:
        host_port, db = host_part.rsplit("/", 1)
        database = int(db) if db else 0
    else:
        host_port = host_part
        database = 0
    
    # Handle port
    if ":" in host_port:
        host, port = host_port.rsplit(":", 1)
        port = int(port)
    else:
        host = host_port
        port = 6379
    
    return RedisSettings(
        host=host,
        port=port,
        password=password,
        database=database,
    )


# File metadata mapping
FILE_METADATA = {
    # TypeScript/JavaScript
    ".tsx": {"type": "tsx", "language": "TypeScript", "framework": "React"},
    ".jsx": {"type": "jsx", "language": "JavaScript", "framework": "React"},
    ".ts": {"type": "ts", "language": "TypeScript", "framework": None},
    ".js": {"type": "js", "language": "JavaScript", "framework": None},
    ".mjs": {"type": "mjs", "language": "JavaScript", "framework": None},
    # Vue
    ".vue": {"type": "vue", "language": "Vue", "framework": "Vue"},
    # Svelte
    ".svelte": {"type": "svelte", "language": "Svelte", "framework": "Svelte"},
    # Python
    ".py": {"type": "py", "language": "Python", "framework": None},
    # Ruby
    ".rb": {"type": "rb", "language": "Ruby", "framework": None},
    ".erb": {"type": "erb", "language": "Ruby", "framework": "Rails"},
    # PHP
    ".php": {"type": "php", "language": "PHP", "framework": None},
    ".blade.php": {"type": "blade", "language": "PHP", "framework": "Laravel"},
    # Go
    ".go": {"type": "go", "language": "Go", "framework": None},
    # Rust
    ".rs": {"type": "rs", "language": "Rust", "framework": None},
    # Java/Kotlin
    ".java": {"type": "java", "language": "Java", "framework": None},
    ".kt": {"type": "kt", "language": "Kotlin", "framework": None},
    # Swift
    ".swift": {"type": "swift", "language": "Swift", "framework": None},
    # C#
    ".cs": {"type": "cs", "language": "C#", "framework": None},
    ".cshtml": {"type": "cshtml", "language": "C#", "framework": "ASP.NET"},
    # HTML templates
    ".html": {"type": "html", "language": "HTML", "framework": None},
    ".htm": {"type": "htm", "language": "HTML", "framework": None},
    # Angular
    ".component.ts": {"type": "ts", "language": "TypeScript", "framework": "Angular"},
}


def _get_file_metadata(file_path: str) -> dict:
    """
    Get file metadata (type, language, framework) based on file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file_type, file_language, file_framework
    """
    file_path_lower = file_path.lower()
    
    # Check for compound extensions first (e.g., .blade.php, .component.ts)
    for ext, metadata in FILE_METADATA.items():
        if file_path_lower.endswith(ext):
            return {
                "file_type": metadata["type"],
                "file_language": metadata["language"],
                "file_framework": metadata["framework"],
            }
    
    # Default: extract extension
    if "." in file_path:
        ext = "." + file_path.rsplit(".", 1)[-1].lower()
        if ext in FILE_METADATA:
            metadata = FILE_METADATA[ext]
            return {
                "file_type": metadata["type"],
                "file_language": metadata["language"],
                "file_framework": metadata["framework"],
            }
    
    return {
        "file_type": None,
        "file_language": None,
        "file_framework": None,
    }


class ScannerService:
    """Service for scanning repositories to find hardcoded strings."""
    
    @staticmethod
    async def cleanup_stale_scans(db: AsyncSession, timeout_minutes: int = 30) -> int:
        """
        Mark very old scanning sessions as failed.
        
        Args:
            db: Database session
            timeout_minutes: Minutes after which a SCANNING session is considered stale
            
        Returns:
            Number of scans cleaned up
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
        
        # Find very old stale scans (SCANNING or PENDING for too long - likely stuck)
        result = await db.execute(
            select(ScanSession).where(
                ScanSession.status.in_([ScanStatus.SCANNING, ScanStatus.PENDING]),
                ScanSession.started_at < cutoff_time
            )
        )
        stale_sessions = list(result.scalars().all())
        
        count = 0
        for session in stale_sessions:
            session.status = ScanStatus.FAILED
            session.error_message = "Scan interrupted. Please start a new scan."
            session.completed_at = datetime.now(timezone.utc)
            count += 1
            logger.warning(f"Marked stale scan {session.id} as FAILED")
        
        if count > 0:
            await db.commit()
            logger.info(f"Cleaned up {count} stale scan sessions")
        
        return count
    
    @staticmethod
    async def get_interrupted_scans(db: AsyncSession) -> list[tuple[int, int]]:
        """
        Get list of interrupted scans that need to be resumed.
        
        Returns:
            List of tuples (scan_session_id, team_id)
        """
        # Find scans that are SCANNING but were started before the server restart
        # These are scans that were interrupted
        result = await db.execute(
            select(ScanSession, Repository)
            .join(Repository, ScanSession.repository_id == Repository.id)
            .where(ScanSession.status == ScanStatus.SCANNING)
        )
        rows = result.all()
        
        interrupted = []
        for session, repository in rows:
            # Get project to find team_id
            from app.models.project import Project
            proj_result = await db.execute(
                select(Project).where(Project.id == repository.project_id)
            )
            project = proj_result.scalar_one_or_none()
            if project:
                interrupted.append((session.id, project.team_id))
                logger.info(f"Found interrupted scan {session.id} for team {project.team_id}")
        
        return interrupted
    
    @staticmethod
    async def start_scan(
        db: AsyncSession,
        repository_id: int,
        user_id: int,
        ai_provider: Optional[str] = None,
        ai_model: Optional[str] = None,
        scan_path: Optional[str] = None,
    ) -> ScanSession:
        """
        Start a new scan session for a repository.
        
        Args:
            db: Database session
            repository_id: Internal repository ID
            user_id: ID of user starting the scan
            ai_provider: AI provider to use (OPENAI or ANTHROPIC)
            ai_model: Specific model to use
            scan_path: Optional directory path to limit scan scope
            
        Returns:
            Created ScanSession
        """
        # Determine AI provider
        provider = AIProvider.ANTHROPIC
        if ai_provider:
            try:
                provider = AIProvider(ai_provider.upper())
            except ValueError:
                provider = AIProvider.ANTHROPIC
        elif settings.scanner_default_provider.upper() == "OPENAI":
            provider = AIProvider.OPENAI
        
        # Determine model
        model = ai_model
        if not model:
            if provider == AIProvider.ANTHROPIC:
                model = settings.anthropic_model
            else:
                model = settings.openai_text_model
        
        # Create scan session
        session = ScanSession(
            repository_id=repository_id,
            started_by_user_id=user_id,
            status=ScanStatus.PENDING,
            ai_provider=provider,
            ai_model=model,
            scan_path=scan_path,
        )
        
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        logger.info(f"Created scan session {session.id} for repository {repository_id}")
        
        return session
    
    @staticmethod
    async def process_scan(
        db: AsyncSession,
        scan_session_id: int,
        team_id: int,
    ) -> bool:
        """
        Process a scan session using arq queue for parallel file analysis.
        
        Args:
            db: Database session
            scan_session_id: Scan session ID
            team_id: Team ID for token usage tracking
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get scan session
            result = await db.execute(
                select(ScanSession).where(ScanSession.id == scan_session_id)
            )
            session = result.scalar_one_or_none()
            
            if not session:
                logger.error(f"Scan session {scan_session_id} not found")
                return False
            
            # Update status to scanning
            session.status = ScanStatus.SCANNING
            session.started_at = datetime.now(timezone.utc)
            await db.commit()
            
            # Get repository info
            result = await db.execute(
                select(Repository).where(Repository.id == session.repository_id)
            )
            repository = result.scalar_one_or_none()
            
            if not repository:
                await ScannerService._fail_scan(db, session, "Repository not found")
                return False
            
            # Get GitHub connection
            result = await db.execute(
                select(GitHubConnection).where(
                    GitHubConnection.id == repository.github_connection_id
                )
            )
            connection = result.scalar_one_or_none()
            
            if not connection:
                await ScannerService._fail_scan(db, session, "GitHub connection not found")
                return False
            
            # Get access token (with auto-refresh)
            access_token = await GitHubService.get_valid_access_token(db, connection)
            if not access_token:
                await ScannerService._fail_scan(db, session, "GitHub token expired. Please reconnect your account.")
                return False
            
            # Get repository file tree
            tree = await GitHubService.get_repository_tree(
                access_token=access_token,
                owner=repository.repo_owner,
                repo=repository.repo_name,
                branch=repository.default_branch or "main",
            )
            
            if not tree:
                await ScannerService._fail_scan(db, session, "Failed to get repository file tree")
                return False
            
            # Filter files by patterns
            include_patterns = repository.source_patterns if repository.source_patterns else None
            files = GitHubService.filter_files_by_patterns(tree, include_patterns)
            
            # Filter by scan_path if specified
            if session.scan_path:
                scan_path_prefix = session.scan_path.rstrip("/") + "/"
                files = [f for f in files if f.get("path", "").startswith(scan_path_prefix)]
                logger.info(f"Filtered to {len(files)} files in directory '{session.scan_path}'")
            
            # Update total files count
            session.files_total = len(files)
            await db.commit()
            
            logger.info(f"Scanning {len(files)} files in repository {repository.full_name}")
            
            # Load existing keys for matching
            existing_keys_map: dict[str, int] = {}  # key_name -> key_id
            if repository.project_id:
                keys_result = await db.execute(
                    select(Key.id, Key.key).where(Key.project_id == repository.project_id)
                )
                for row in keys_result.fetchall():
                    existing_keys_map[row[1]] = row[0]  # key name -> key id
                logger.info(f"Loaded {len(existing_keys_map)} existing keys for matching")
            
            # Connect to Redis and create job pool
            try:
                redis_pool = await create_pool(_get_redis_settings())
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {type(e).__name__}: {str(e)}")
                await ScannerService._fail_scan(db, session, "Failed to connect to job queue")
                return False
            
            # Get already processed files (for resume after restart)
            already_processed = set(session.processed_files or [])
            if already_processed:
                logger.info(f"Resuming scan {scan_session_id}: {len(already_processed)} files already processed")
            
            # Enqueue jobs for files that haven't been processed yet
            jobs = []
            skipped_count = 0
            for file_entry in files:
                file_path = file_entry.get("path", "")
                
                # Skip already processed files (for resume)
                if file_path in already_processed:
                    skipped_count += 1
                    continue
                
                try:
                    # Get file content
                    content = await GitHubService.get_file_content(
                        access_token=access_token,
                        owner=repository.repo_owner,
                        repo=repository.repo_name,
                        path=file_path,
                        branch=repository.default_branch or "main",
                    )
                    
                    if content is None:
                        logger.warning(f"Could not get content for {file_path}")
                        continue
                    
                    # Skip empty files or files that are too large
                    if not content or len(content) > 100000:  # 100KB limit
                        continue
                    
                    # Enqueue job with provider and model from session
                    job = await redis_pool.enqueue_job(
                        "analyze_file_task",
                        file_path,
                        content,
                        scan_session_id,
                        repository.i18n_framework,
                        session.ai_provider.value,  # Pass provider
                        session.ai_model,  # Pass model
                    )
                    jobs.append((file_path, job))
                    
                except Exception as e:
                    logger.error(f"Error enqueueing job for {file_path}: {type(e).__name__}: {str(e)}")
                    continue
            
            if skipped_count > 0:
                logger.info(f"Skipped {skipped_count} already processed files")
            
            logger.info(f"Enqueued {len(jobs)} jobs for scan session {scan_session_id}")
            
            # Wait for results and process them
            total_strings = 0
            files_processed = 0
            
            for file_path, job in jobs:
                # Check if scan was cancelled (fresh query to see changes from other transactions)
                status_result = await db.execute(
                    select(ScanSession.status).where(ScanSession.id == scan_session_id)
                )
                current_status = status_result.scalar_one_or_none()
                if current_status == ScanStatus.CANCELLED:
                    logger.info(f"Scan {scan_session_id} was cancelled, stopping processing")
                    # Cancel remaining jobs (they will timeout)
                    await redis_pool.close()
                    return False
                
                try:
                    # Wait for job result with timeout
                    result = await job.result(timeout=settings.scanner_job_timeout)
                    
                    if result and result.get("success"):
                        strings = result.get("strings", [])
                        token_usage = result.get("token_usage", {})
                        
                        # Record token usage
                        if token_usage and token_usage.get("total_tokens", 0) > 0:
                            await TokenUsageService.record_usage(
                                db=db,
                                team_id=team_id,
                                user_id=session.started_by_user_id,
                                operation_type="SCAN_FILE",
                                provider=session.ai_provider.value,
                                model=session.ai_model,
                                input_tokens=token_usage.get("input_tokens", 0),
                                output_tokens=token_usage.get("output_tokens", 0),
                                scan_session_id=session.id,
                            )
                        
                        # Save found strings
                        # Get file metadata once per file
                        file_metadata = _get_file_metadata(file_path)
                        
                        for string_info in strings:
                            suggested_key = string_info.get("suggested_key", "")
                            
                            # Check if key with this name already exists
                            matched_key_id = existing_keys_map.get(suggested_key)
                            status = FoundStringStatus.MATCHED if matched_key_id else FoundStringStatus.PENDING
                            
                            found_string = FoundString(
                                scan_session_id=session.id,
                                file_path=file_path,
                                line_number=string_info.get("line"),
                                original_text=string_info.get("text", ""),
                                suggested_key=suggested_key,
                                context=string_info.get("context", ""),
                                confidence=int(string_info.get("confidence", 0.8) * 100),
                                status=status,
                                matched_key_id=matched_key_id,
                                file_type=file_metadata["file_type"],
                                file_language=file_metadata["file_language"],
                                file_framework=file_metadata["file_framework"],
                            )
                            db.add(found_string)
                        
                        total_strings += len(strings)
                        
                    # Mark file as processed (for resume)
                    if session.processed_files is None:
                        session.processed_files = []
                    session.processed_files = session.processed_files + [file_path]
                        
                except asyncio.TimeoutError:
                    logger.error(f"Job timeout for {file_path}")
                except Exception as e:
                    logger.error(f"Error getting job result for {file_path}: {type(e).__name__}: {str(e)}")
                
                files_processed += 1
                
                # Update progress periodically (every 5 files) and check for cancellation
                if files_processed % 5 == 0:
                    # Check if cancelled
                    status_check = await db.execute(
                        select(ScanSession.status).where(ScanSession.id == scan_session_id)
                    )
                    if status_check.scalar_one_or_none() == ScanStatus.CANCELLED:
                        logger.info(f"Scan {scan_session_id} was cancelled during processing")
                        await redis_pool.close()
                        return False
                    
                    session.files_scanned = len(session.processed_files or [])
                    session.strings_found = total_strings
                    await db.commit()
            
            # Close Redis pool
            await redis_pool.close()
            
            # Mark as completed
            session.status = ScanStatus.COMPLETED
            session.completed_at = datetime.now(timezone.utc)
            session.files_scanned = len(session.processed_files or [])
            session.strings_found = total_strings
            await db.commit()
            
            logger.info(f"Scan {scan_session_id} completed: {total_strings} strings found in {files_processed} files")
            
            # Log scan completion activity
            proj_result = await db.execute(
                select(Project).where(Project.id == repository.project_id)
            )
            project = proj_result.scalar_one_or_none()
            if project:
                scan_complete_log = ActivityLog(
                    team_id=project.team_id,
                    project_id=project.id,
                    user_id=session.started_by_user_id,
                    action=ActionType.SCAN_COMPLETE,
                    extra_data={
                        "repository": repository.full_name,
                        "files_scanned": files_processed,
                        "strings_found": total_strings,
                        "scan_session_id": str(session.public_id),
                    }
                )
                db.add(scan_complete_log)
                await db.commit()
            
            # Send email notification to user who started the scan
            await ScannerService._send_completion_email(
                db=db,
                session=session,
                repository=repository,
                files_scanned=files_processed,
                strings_found=total_strings,
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Scan error: {type(e).__name__}: {str(e)}")
            try:
                result = await db.execute(
                    select(ScanSession).where(ScanSession.id == scan_session_id)
                )
                session = result.scalar_one_or_none()
                if session:
                    await ScannerService._fail_scan(db, session, str(e))
            except Exception:
                pass
            return False
    
    @staticmethod
    async def _get_existing_keys(db: AsyncSession, project_id: int) -> list[str]:
        """Get list of existing translation keys in the project."""
        result = await db.execute(
            select(Key.key).where(Key.project_id == project_id)
        )
        return [row[0] for row in result.fetchall()]
    
    @staticmethod
    async def _fail_scan(db: AsyncSession, session: ScanSession, error_message: str):
        """Mark a scan session as failed."""
        session.status = ScanStatus.FAILED
        session.error_message = error_message
        session.completed_at = datetime.now(timezone.utc)
        await db.commit()
        logger.error(f"Scan {session.id} failed: {error_message}")
        
        # Log scan failure activity
        try:
            result = await db.execute(
                select(Repository).where(Repository.id == session.repository_id)
            )
            repository = result.scalar_one_or_none()
            if repository:
                proj_result = await db.execute(
                    select(Project).where(Project.id == repository.project_id)
                )
                project = proj_result.scalar_one_or_none()
                if project:
                    scan_failed_log = ActivityLog(
                        team_id=project.team_id,
                        project_id=project.id,
                        user_id=session.started_by_user_id,
                        action=ActionType.SCAN_FAILED,
                        extra_data={
                            "repository": repository.full_name,
                            "error": error_message,
                            "scan_session_id": str(session.public_id),
                        }
                    )
                    db.add(scan_failed_log)
                    await db.commit()
        except Exception as e:
            logger.warning(f"Failed to log scan failure: {type(e).__name__}: {str(e)}")
    
    @staticmethod
    async def _send_completion_email(
        db: AsyncSession,
        session: ScanSession,
        repository: Repository,
        files_scanned: int,
        strings_found: int,
    ):
        """Send email notification when scan completes."""
        try:
            # Get user who started the scan
            if not session.started_by_user_id:
                logger.warning(f"No user ID for scan {session.id}, skipping email")
                return
            
            result = await db.execute(
                select(User).where(User.id == session.started_by_user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.email:
                logger.warning(f"User not found for scan {session.id}, skipping email")
                return
            
            # Get project name
            result = await db.execute(
                select(Project).where(Project.id == repository.project_id)
            )
            project = result.scalar_one_or_none()
            project_name = project.name if project else "Unknown Project"
            
            # Build scan URL
            project_public_id = str(project.public_id) if project else ""
            scan_url = f"{settings.app_url}/project/{project_public_id}/scanner"
            
            # Send email in background thread
            send_scan_completed_email_background(
                email=user.email,
                username=user.username or user.email,
                project_name=project_name,
                files_scanned=files_scanned,
                strings_found=strings_found,
                status=session.status.value,
                scan_url=scan_url,
            )
            
            logger.info(f"Scan completion email queued for {user.email}")
            
        except Exception as e:
            # Don't fail the scan if email fails
            logger.error(f"Failed to send scan completion email: {type(e).__name__}: {str(e)}")
    
    @staticmethod
    async def cancel_scan(db: AsyncSession, scan_session_id: int) -> bool:
        """
        Cancel a running scan.
        
        Sets cancel flag in Redis so workers stop immediately.
        
        Args:
            db: Database session
            scan_session_id: Scan session ID
            
        Returns:
            True if cancelled, False otherwise
        """
        result = await db.execute(
            select(ScanSession).where(ScanSession.id == scan_session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return False
        
        if session.status not in [ScanStatus.PENDING, ScanStatus.SCANNING]:
            return False
        
        # Set cancel flag in Redis (workers check this before AI calls)
        try:
            from redis.asyncio import Redis as AsyncRedis
            redis_settings = _get_redis_settings()
            redis_client = AsyncRedis(
                host=redis_settings.host,
                port=redis_settings.port,
                password=redis_settings.password,
                db=redis_settings.database,
            )
            # Set flag with 1 hour TTL (in case cleanup doesn't happen)
            await redis_client.set(f"scan_cancelled:{scan_session_id}", "1", ex=3600)
            await redis_client.close()
            logger.info(f"Set cancel flag in Redis for scan {scan_session_id}")
        except Exception as e:
            logger.warning(f"Failed to set Redis cancel flag: {type(e).__name__}: {str(e)}")
        
        session.status = ScanStatus.CANCELLED
        session.completed_at = datetime.now(timezone.utc)
        await db.commit()
        
        logger.info(f"Scan {scan_session_id} cancelled")
        return True
    
    @staticmethod
    async def get_scan_session(
        db: AsyncSession,
        public_id: str,
    ) -> Optional[ScanSession]:
        """Get a scan session by public ID."""
        try:
            uuid_obj = UUID(public_id)
            result = await db.execute(
                select(ScanSession).where(ScanSession.public_id == uuid_obj)
            )
            return result.scalar_one_or_none()
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    async def get_scan_session_by_id(
        db: AsyncSession,
        session_id: int,
    ) -> Optional[ScanSession]:
        """Get a scan session by internal ID."""
        result = await db.execute(
            select(ScanSession).where(ScanSession.id == session_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_scan_sessions_by_repository(
        db: AsyncSession,
        repository_id: int,
        limit: int = 10,
    ) -> list[ScanSession]:
        """Get recent scan sessions for a repository."""
        result = await db.execute(
            select(ScanSession)
            .where(ScanSession.repository_id == repository_id)
            .order_by(ScanSession.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_found_strings(
        db: AsyncSession,
        scan_session_id: int,
        status: Optional[FoundStringStatus] = None,
    ) -> list[FoundString]:
        """Get found strings for a scan session."""
        query = (
            select(FoundString)
            .where(FoundString.scan_session_id == scan_session_id)
            .options(
                joinedload(FoundString.key),
                joinedload(FoundString.matched_key),
            )
        )
        
        if status:
            query = query.where(FoundString.status == status)
        
        query = query.order_by(FoundString.file_path, FoundString.line_number)
        
        result = await db.execute(query)
        return list(result.scalars().unique().all())
    
    @staticmethod
    async def update_found_string_status(
        db: AsyncSession,
        found_string_id: int,
        status: FoundStringStatus,
    ) -> Optional[FoundString]:
        """Update the status of a found string."""
        result = await db.execute(
            select(FoundString).where(FoundString.id == found_string_id)
        )
        found_string = result.scalar_one_or_none()
        
        if not found_string:
            return None
        
        found_string.status = status
        await db.commit()
        await db.refresh(found_string)
        
        return found_string
    
    @staticmethod
    async def convert_found_strings_to_keys(
        db: AsyncSession,
        scan_session_id: int,
        project_id: int,
        default_language: str = "en",
    ) -> int:
        """
        Convert approved found strings to translation keys.
        
        Args:
            db: Database session
            scan_session_id: Scan session ID
            project_id: Project ID to create keys in
            default_language: Default language for initial translation
            
        Returns:
            Number of keys created
        """
        # Get approved found strings
        result = await db.execute(
            select(FoundString)
            .where(
                FoundString.scan_session_id == scan_session_id,
                FoundString.status == FoundStringStatus.APPROVED,
            )
        )
        found_strings = list(result.scalars().all())
        
        if not found_strings:
            return 0
        
        # Get existing keys to avoid duplicates
        existing_keys = await ScannerService._get_existing_keys(db, project_id)
        existing_keys_set = set(existing_keys)
        
        created_count = 0
        
        for found_string in found_strings:
            # Skip if key already exists
            if found_string.suggested_key in existing_keys_set:
                logger.warning(f"Key {found_string.suggested_key} already exists, skipping")
                continue
            
            # Create the key
            key = Key(
                project_id=project_id,
                key=found_string.suggested_key,
                description=found_string.context,
            )
            db.add(key)
            await db.flush()  # Get the key ID
            
            # Create initial translation
            translation = Translation(
                key_id=key.id,
                language=default_language,
                value=found_string.original_text,
            )
            db.add(translation)
            
            # Update found string
            found_string.status = FoundStringStatus.CONVERTED
            found_string.key_id = key.id
            
            existing_keys_set.add(found_string.suggested_key)
            created_count += 1
        
        await db.commit()
        
        logger.info(f"Created {created_count} keys from scan session {scan_session_id}")
        return created_count
