"""
Scanner Service for repository code analysis.
Handles the scanning of repositories to find hardcoded strings.
Uses arq (Redis queue) for background processing.
"""
import asyncio
import logging
from typing import Optional, Any
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from arq import create_pool
from arq.connections import RedisSettings

from app.models.scan_session import ScanSession, ScanStatus, AIProvider
from app.models.found_string import FoundString, FoundStringStatus
from app.models.repository import Repository
from app.models.github_connection import GitHubConnection
from app.models.key import Key, Translation
from app.services.github_service import GitHubService
from app.services.token_usage_service import TokenUsageService
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


class ScannerService:
    """Service for scanning repositories to find hardcoded strings."""
    
    @staticmethod
    async def start_scan(
        db: AsyncSession,
        repository_id: int,
        user_id: int,
        ai_provider: Optional[str] = None,
        ai_model: Optional[str] = None,
    ) -> ScanSession:
        """
        Start a new scan session for a repository.
        
        Args:
            db: Database session
            repository_id: Internal repository ID
            user_id: ID of user starting the scan
            ai_provider: AI provider to use (OPENAI or ANTHROPIC)
            ai_model: Specific model to use
            
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
            session.started_at = datetime.utcnow()
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
            
            # Get access token
            access_token = GitHubService.get_decrypted_token(connection)
            
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
            
            # Update total files count
            session.files_total = len(files)
            await db.commit()
            
            logger.info(f"Scanning {len(files)} files in repository {repository.full_name}")
            
            # Connect to Redis and create job pool
            try:
                redis_pool = await create_pool(_get_redis_settings())
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {type(e).__name__}: {str(e)}")
                await ScannerService._fail_scan(db, session, "Failed to connect to job queue")
                return False
            
            # Enqueue jobs for all files
            jobs = []
            for file_entry in files:
                file_path = file_entry.get("path", "")
                
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
                    
                    # Enqueue job
                    job = await redis_pool.enqueue_job(
                        "analyze_file_task",
                        file_path,
                        content,
                        scan_session_id,
                        repository.i18n_framework,
                    )
                    jobs.append((file_path, job))
                    
                except Exception as e:
                    logger.error(f"Error enqueueing job for {file_path}: {type(e).__name__}: {str(e)}")
                    continue
            
            logger.info(f"Enqueued {len(jobs)} jobs for scan session {scan_session_id}")
            
            # Wait for results and process them
            total_strings = 0
            files_processed = 0
            
            for file_path, job in jobs:
                # Check if scan was cancelled
                await db.refresh(session)
                if session.status == ScanStatus.CANCELLED:
                    logger.info(f"Scan {scan_session_id} was cancelled")
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
                        for string_info in strings:
                            found_string = FoundString(
                                scan_session_id=session.id,
                                file_path=file_path,
                                line_number=string_info.get("line"),
                                original_text=string_info.get("text", ""),
                                suggested_key=string_info.get("suggested_key", ""),
                                context=string_info.get("context", ""),
                                confidence=int(string_info.get("confidence", 0.8) * 100),
                                status=FoundStringStatus.PENDING,
                            )
                            db.add(found_string)
                        
                        total_strings += len(strings)
                        
                except asyncio.TimeoutError:
                    logger.error(f"Job timeout for {file_path}")
                except Exception as e:
                    logger.error(f"Error getting job result for {file_path}: {type(e).__name__}: {str(e)}")
                
                files_processed += 1
                
                # Update progress periodically (every 5 files)
                if files_processed % 5 == 0:
                    session.files_scanned = files_processed
                    session.strings_found = total_strings
                    await db.commit()
            
            # Close Redis pool
            await redis_pool.close()
            
            # Mark as completed
            session.status = ScanStatus.COMPLETED
            session.completed_at = datetime.utcnow()
            session.files_scanned = files_processed
            session.strings_found = total_strings
            await db.commit()
            
            logger.info(f"Scan {scan_session_id} completed: {total_strings} strings found in {files_processed} files")
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
        session.completed_at = datetime.utcnow()
        await db.commit()
        logger.error(f"Scan {session.id} failed: {error_message}")
    
    @staticmethod
    async def cancel_scan(db: AsyncSession, scan_session_id: int) -> bool:
        """
        Cancel a running scan.
        
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
        
        session.status = ScanStatus.CANCELLED
        session.completed_at = datetime.utcnow()
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
        query = select(FoundString).where(FoundString.scan_session_id == scan_session_id)
        
        if status:
            query = query.where(FoundString.status == status)
        
        query = query.order_by(FoundString.file_path, FoundString.line_number)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
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
