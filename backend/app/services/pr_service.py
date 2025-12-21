"""
PR Service for handling pull request creation in background.
Supports recovery after server restart.
"""
import asyncio
import logging
import time
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified
from arq import create_pool
from arq.connections import RedisSettings

from app.models.scan_session import ScanSession, PRStatus
from app.models.found_string import FoundString, FoundStringStatus
from app.models.repository import Repository
from app.models.github_connection import GitHubConnection
from app.models.key import Key
from app.services.github_service import GitHubService
from app.services.scanner_service import ScannerService
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


class PRService:
    """Service for creating pull requests in background."""
    
    @staticmethod
    async def start_pr_creation(
        db: AsyncSession,
        scan_session_id: int,
        translation_function: str = "t",
    ) -> tuple[bool, str]:
        """
        Start PR creation process in background.
        
        Args:
            db: Database session
            scan_session_id: ID of the scan session
            translation_function: Name of the translation function (default: "t")
            
        Returns:
            Tuple of (success, message)
        """
        # Get scan session
        result = await db.execute(
            select(ScanSession).where(ScanSession.id == scan_session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return False, "Scan session not found"
        
        # Check if PR is already in progress or completed
        if session.pr_status == PRStatus.PROCESSING:
            return False, "PR creation already in progress"
        
        if session.pr_url:
            return False, f"Pull request already created: {session.pr_url}"
        
        # Get found strings ready for PR
        found_strings = await ScannerService.get_found_strings(db, session.id)
        ready_strings = [
            fs for fs in found_strings 
            if (fs.status == FoundStringStatus.CONVERTED and fs.key_id) or
               (fs.status == FoundStringStatus.MATCHED and fs.matched_key_id)
        ]
        
        if not ready_strings:
            return False, "No keys ready for PR. Please convert approved strings to keys first."
        
        # Group strings by file
        files_to_modify = {}
        for fs in ready_strings:
            if fs.file_path not in files_to_modify:
                files_to_modify[fs.file_path] = []
            files_to_modify[fs.file_path].append(fs)
        
        # Update session with PR status
        session.pr_status = PRStatus.PENDING
        session.pr_translation_function = translation_function
        session.pr_files_total = len(files_to_modify)
        session.pr_files_processed = 0
        session.pr_processed_files = []
        session.pr_error_message = None
        await db.commit()
        
        logger.info(f"Started PR creation for session {scan_session_id} with {len(files_to_modify)} files")
        
        return True, f"PR creation started for {len(files_to_modify)} files"
    
    @staticmethod
    async def process_pr(
        db: AsyncSession,
        scan_session_id: int,
    ) -> bool:
        """
        Process PR creation for a scan session.
        Uses arq queue for processing files.
        
        Args:
            db: Database session
            scan_session_id: Scan session ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"PR process_pr started for session {scan_session_id}")
            
            # Get scan session
            result = await db.execute(
                select(ScanSession).where(ScanSession.id == scan_session_id)
            )
            session = result.scalar_one_or_none()
            
            if not session:
                logger.error(f"Scan session {scan_session_id} not found")
                return False
            
            logger.info(f"PR {scan_session_id}: Found session, updating status to PROCESSING")
            
            # Update status to processing
            session.pr_status = PRStatus.PROCESSING
            await db.commit()
            
            logger.info(f"PR {scan_session_id}: Status updated to PROCESSING")
            
            # Get repository
            result = await db.execute(
                select(Repository).where(Repository.id == session.repository_id)
            )
            repository = result.scalar_one_or_none()
            
            if not repository:
                await PRService._fail_pr(db, session, "Repository not found")
                return False
            
            # Get GitHub connection
            result = await db.execute(
                select(GitHubConnection).where(
                    GitHubConnection.id == repository.github_connection_id
                )
            )
            connection = result.scalar_one_or_none()
            
            if not connection:
                await PRService._fail_pr(db, session, "GitHub connection not found")
                return False
            
            # Get access token
            logger.info(f"PR {scan_session_id}: Getting access token...")
            access_token = await GitHubService.get_valid_access_token(db, connection)
            if not access_token:
                await PRService._fail_pr(db, session, "GitHub token expired. Please reconnect your account.")
                return False
            
            logger.info(f"PR {scan_session_id}: Got access token, fetching found strings...")
            
            # Get found strings ready for PR
            found_strings = await ScannerService.get_found_strings(db, session.id)
            ready_strings = [
                fs for fs in found_strings 
                if (fs.status == FoundStringStatus.CONVERTED and fs.key_id) or
                   (fs.status == FoundStringStatus.MATCHED and fs.matched_key_id)
            ]
            
            logger.info(f"PR {scan_session_id}: Found {len(ready_strings)} ready strings out of {len(found_strings)} total")
            
            if not ready_strings:
                await PRService._fail_pr(db, session, "No keys ready for PR")
                return False
            
            # Load keys for all strings
            key_ids = set()
            for fs in ready_strings:
                if fs.key_id:
                    key_ids.add(fs.key_id)
                if fs.matched_key_id:
                    key_ids.add(fs.matched_key_id)
            
            keys_result = await db.execute(
                select(Key).where(Key.id.in_(list(key_ids)))
            )
            keys_map = {key.id: key for key in keys_result.scalars().all()}
            
            # Group strings by file
            files_to_modify: dict[str, list] = {}
            for fs in ready_strings:
                if fs.file_path not in files_to_modify:
                    files_to_modify[fs.file_path] = []
                files_to_modify[fs.file_path].append(fs)
            
            # Create branch name
            branch_name = f"localization/scan-{int(time.time())}"
            
            # Create branch (or get existing one if resuming)
            if not session.pr_branch_name:
                logger.info(f"PR {scan_session_id}: Creating branch {branch_name}...")
                branch_sha = await GitHubService.create_branch(
                    access_token=access_token,
                    owner=repository.repo_owner,
                    repo=repository.repo_name,
                    branch_name=branch_name,
                    source_branch=repository.default_branch or "main",
                )
                
                if not branch_sha:
                    await PRService._fail_pr(db, session, "Failed to create branch. Please check repository permissions.")
                    return False
                
                logger.info(f"PR {scan_session_id}: Branch created: {branch_name}")
                session.pr_branch_name = branch_name
                await db.commit()
            else:
                # Resume with existing branch
                branch_name = session.pr_branch_name
                logger.info(f"PR {scan_session_id}: Resuming with existing branch: {branch_name}")
            
            # Connect to Redis for job queue
            try:
                logger.info(f"Connecting to Redis for PR {scan_session_id}...")
                redis_pool = await create_pool(_get_redis_settings())
                logger.info(f"Connected to Redis for PR {scan_session_id}")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {type(e).__name__}: {str(e)}")
                await PRService._fail_pr(db, session, "Failed to connect to job queue")
                return False
            
            # Get already processed files (for resume after restart)
            already_processed = set(session.pr_processed_files or [])
            if already_processed:
                logger.info(f"Resuming PR creation {scan_session_id}: {len(already_processed)} files already processed")
            
            # Process files
            files_modified = 0
            translation_function = session.pr_translation_function or "t"
            
            logger.info(f"PR {scan_session_id}: Processing {len(files_to_modify)} files...")
            
            for file_path, strings in files_to_modify.items():
                # Skip already processed files
                if file_path in already_processed:
                    continue
                
                # Check if PR was cancelled
                status_result = await db.execute(
                    select(ScanSession.pr_status).where(ScanSession.id == scan_session_id)
                )
                current_status = status_result.scalar_one_or_none()
                if current_status != PRStatus.PROCESSING:
                    logger.info(f"PR creation {scan_session_id} was stopped (status: {current_status})")
                    await redis_pool.close()
                    return False
                
                try:
                    # Get current file content
                    content = await GitHubService.get_file_content(
                        access_token=access_token,
                        owner=repository.repo_owner,
                        repo=repository.repo_name,
                        path=file_path,
                        branch=repository.default_branch or "main",
                    )
                    
                    if content is None:
                        logger.warning(f"Could not get content for file: {file_path}")
                        continue
                    
                    # Get file SHA for the branch
                    file_sha = await GitHubService.get_file_sha(
                        access_token=access_token,
                        owner=repository.repo_owner,
                        repo=repository.repo_name,
                        path=file_path,
                        branch=branch_name,
                    )
                    
                    # Build replacements list
                    replacements = []
                    for fs in strings:
                        key_id_to_use = fs.key_id if fs.key_id else fs.matched_key_id
                        key = keys_map.get(key_id_to_use) if key_id_to_use else None
                        if not key:
                            continue
                        
                        replacements.append({
                            "original_text": fs.original_text,
                            "key": key.key,
                            "line_number": fs.line_number,
                        })
                    
                    if not replacements:
                        continue
                    
                    # Enqueue job for file processing
                    logger.info(f"PR {scan_session_id}: Enqueueing job for {file_path} ({len(replacements)} replacements)")
                    job = await redis_pool.enqueue_job(
                        "process_pr_file_task",
                        file_path,
                        content,
                        file_sha,
                        replacements,
                        scan_session_id,
                        translation_function,
                        session.ai_provider.value,
                        session.ai_model,
                        repository.repo_owner,
                        repository.repo_name,
                        branch_name,
                        access_token,
                    )
                    
                    # Wait for result
                    logger.info(f"PR {scan_session_id}: Waiting for job result for {file_path}...")
                    job_result = await job.result(timeout=settings.scanner_job_timeout)
                    logger.info(f"PR {scan_session_id}: Got job result for {file_path}: {job_result}")
                    
                    if job_result is None:
                        logger.error(f"PR {scan_session_id}: Job result is None for {file_path} - worker may not be running!")
                    elif job_result.get("success"):
                        if job_result.get("modified"):
                            files_modified += 1
                            logger.info(f"Successfully modified {file_path}")
                    elif job_result.get("cancelled"):
                        logger.info(f"PR creation {scan_session_id} was cancelled")
                        await redis_pool.close()
                        return False
                    else:
                        logger.warning(f"Failed to process {file_path}: {job_result.get('error', 'Unknown error')}")
                    
                    # Mark file as processed
                    if session.pr_processed_files is None:
                        session.pr_processed_files = []
                    session.pr_processed_files = session.pr_processed_files + [file_path]
                    flag_modified(session, "pr_processed_files")
                    
                    session.pr_files_processed = len(session.pr_processed_files)
                    await db.commit()
                    logger.info(f"PR {scan_session_id}: Progress {session.pr_files_processed}/{session.pr_files_total}")
                    
                except asyncio.TimeoutError:
                    logger.error(f"Job timeout for {file_path}")
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {type(e).__name__}: {str(e)}")
            
            # Close Redis pool
            await redis_pool.close()
            
            if files_modified == 0:
                await PRService._fail_pr(db, session, "No files were modified. Strings may have already been replaced.")
                return False
            
            # Create PR
            pr_title = f"🌐 Add localization keys ({files_modified} files)"
            pr_body = PRService._build_pr_body(ready_strings, keys_map, files_modified, translation_function)
            
            pr_data = await GitHubService.create_pull_request(
                access_token=access_token,
                owner=repository.repo_owner,
                repo=repository.repo_name,
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=repository.default_branch or "main",
            )
            
            if not pr_data:
                await PRService._fail_pr(
                    db, session, 
                    "Failed to create pull request. Branch was created but PR creation failed."
                )
                return False
            
            # Update scan session with PR info
            session.pr_status = PRStatus.COMPLETED
            session.pr_number = pr_data.get("number")
            session.pr_url = pr_data.get("html_url")
            session.pr_created_at = datetime.now(timezone.utc)
            await db.commit()
            
            logger.info(f"PR created successfully: {session.pr_url}")
            return True
            
        except Exception as e:
            logger.error(f"PR creation error: {type(e).__name__}: {str(e)}")
            try:
                result = await db.execute(
                    select(ScanSession).where(ScanSession.id == scan_session_id)
                )
                session = result.scalar_one_or_none()
                if session:
                    await PRService._fail_pr(db, session, str(e))
            except Exception:
                pass
            return False
    
    @staticmethod
    def _build_pr_body(
        ready_strings: list[FoundString],
        keys_map: dict[int, Key],
        files_modified: int,
        translation_function: str,
    ) -> str:
        """Build PR description body."""
        pr_body = f"""## Localization Changes

This PR replaces hardcoded strings with translation function calls.

### Summary
- **Files modified:** {files_modified}
- **Keys used:** {len(ready_strings)}
- **Translation function:** `{translation_function}()`

### Changes
The following strings have been replaced with translation keys:

| File | Key | Original Text |
|------|-----|---------------|
"""
        for fs in ready_strings[:20]:  # Limit to first 20
            key_id_to_use = fs.key_id if fs.key_id else fs.matched_key_id
            key = keys_map.get(key_id_to_use) if key_id_to_use else None
            if key:
                # Truncate long strings
                text = fs.original_text[:50] + "..." if len(fs.original_text) > 50 else fs.original_text
                pr_body += f"| `{fs.file_path.split('/')[-1]}` | `{key.key}` | {text} |\n"
        
        if len(ready_strings) > 20:
            pr_body += f"\n_...and {len(ready_strings) - 20} more_\n"
        
        pr_body += """
---
_Generated automatically by Keeys localization scanner_
"""
        return pr_body
    
    @staticmethod
    async def _fail_pr(db: AsyncSession, session: ScanSession, error_message: str):
        """Mark PR creation as failed."""
        session.pr_status = PRStatus.FAILED
        session.pr_error_message = error_message
        await db.commit()
        logger.error(f"PR creation {session.id} failed: {error_message}")
    
    @staticmethod
    async def cancel_pr(db: AsyncSession, scan_session_id: int) -> bool:
        """
        Cancel PR creation in progress.
        
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
        
        if session.pr_status != PRStatus.PROCESSING:
            return False
        
        # Set cancel flag in Redis
        try:
            from redis.asyncio import Redis as AsyncRedis
            redis_settings = _get_redis_settings()
            redis_client = AsyncRedis(
                host=redis_settings.host,
                port=redis_settings.port,
                password=redis_settings.password,
                db=redis_settings.database,
            )
            await redis_client.set(f"pr_cancelled:{scan_session_id}", "1", ex=3600)
            await redis_client.close()
            logger.info(f"Set cancel flag in Redis for PR {scan_session_id}")
        except Exception as e:
            logger.warning(f"Failed to set Redis cancel flag: {type(e).__name__}: {str(e)}")
        
        session.pr_status = PRStatus.FAILED
        session.pr_error_message = "PR creation cancelled by user"
        await db.commit()
        
        logger.info(f"PR creation {scan_session_id} cancelled")
        return True
    
    @staticmethod
    async def get_interrupted_pr_creations(db: AsyncSession) -> list[int]:
        """
        Get list of interrupted PR creations that need to be resumed.
        
        Returns:
            List of scan_session_ids with interrupted PR creation
        """
        result = await db.execute(
            select(ScanSession)
            .where(ScanSession.pr_status == PRStatus.PROCESSING)
        )
        sessions = result.scalars().all()
        
        interrupted = []
        for session in sessions:
            interrupted.append(session.id)
            logger.info(f"Found interrupted PR creation: session {session.id}")
        
        return interrupted
    
    @staticmethod
    async def cleanup_stale_pr_creations(db: AsyncSession, timeout_minutes: int = 60) -> int:
        """
        Mark very old PR creations as failed.
        
        Args:
            db: Database session
            timeout_minutes: Minutes after which a PROCESSING PR is considered stale
            
        Returns:
            Number of PR creations cleaned up
        """
        from datetime import timedelta
        
        # PR creations don't have a started_at, so we check against session's started_at
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
        
        result = await db.execute(
            select(ScanSession).where(
                ScanSession.pr_status == PRStatus.PROCESSING,
                ScanSession.started_at < cutoff_time
            )
        )
        stale_sessions = list(result.scalars().all())
        
        count = 0
        for session in stale_sessions:
            session.pr_status = PRStatus.FAILED
            session.pr_error_message = "PR creation interrupted. Please try again."
            count += 1
            logger.warning(f"Marked stale PR creation {session.id} as FAILED")
        
        if count > 0:
            await db.commit()
            logger.info(f"Cleaned up {count} stale PR creations")
        
        return count

