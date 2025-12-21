"""
ARQ Worker for background file analysis tasks.

Run with: arq worker.WorkerSettings

Supports two types of tasks:
1. analyze_file_task - Analyze a single file for hardcoded strings (used in scanning)
2. process_pr_file_task - Process a single file for PR creation (replace strings with keys)
"""
import logging
import sys
from typing import Optional, Any
from arq import create_pool
from arq.connections import RedisSettings
from redis.asyncio import Redis

from app.core.config import settings
from app.services.ai_service import ai_service, AnalysisResult

# Configure ALL logging to stdout (Railway shows stderr as red)
# Remove all existing handlers and redirect everything to stdout
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
root_logger.addHandler(stdout_handler)

# Also configure arq logger specifically
logging.getLogger('arq').handlers = []
logging.getLogger('arq').addHandler(stdout_handler)
logging.getLogger('arq.worker').handlers = []
logging.getLogger('arq.worker').addHandler(stdout_handler)

logger = logging.getLogger(__name__)


def get_redis_settings() -> RedisSettings:
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


async def analyze_file_task(
    ctx: dict,
    file_path: str,
    file_content: str,
    scan_session_id: int,
    i18n_framework: Optional[str] = None,
    ai_provider: Optional[str] = None,
    ai_model: Optional[str] = None,
    key_naming_style: Optional[str] = None,
    key_naming_delimiter: Optional[str] = None,
) -> dict[str, Any]:
    """
    Analyze a single file for hardcoded strings.
    
    Args:
        ctx: ARQ context (contains redis connection)
        file_path: Path to the file in the repository
        file_content: Content of the file
        scan_session_id: ID of the scan session
        i18n_framework: Optional i18n framework name
        ai_provider: AI provider to use (OPENAI or ANTHROPIC)
        ai_model: Specific AI model to use
        key_naming_style: Key naming style (UPPERCASE, snake_case, camelCase)
        key_naming_delimiter: Delimiter for key segments (_, ., :, ::)
        
    Returns:
        Dictionary with analysis results:
        - file_path: str
        - strings: list of found strings
        - token_usage: dict with input/output/total tokens
        - scan_session_id: int
        - success: bool
        - error: optional error message
    """
    logger.info(f"Analyzing file: {file_path} for session {scan_session_id} with {ai_provider}/{ai_model}")
    
    try:
        # Check Redis cancel flag BEFORE calling AI (instant, no DB query)
        cancel_redis = ctx.get('cancel_redis')
        if cancel_redis:
            try:
                cancel_key = f"scan_cancelled:{scan_session_id}"
                cancelled = await cancel_redis.get(cancel_key)
                logger.debug(f"Cancel check for {cancel_key}: {cancelled}")
                if cancelled:
                    logger.info(f"🛑 Scan {scan_session_id} was cancelled, skipping file {file_path}")
                    return {
                        "file_path": file_path,
                        "strings": [],
                        "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
                        "scan_session_id": scan_session_id,
                        "success": False,
                        "error": "Scan cancelled",
                        "cancelled": True,
                    }
            except Exception as e:
                logger.warning(f"Failed to check cancel flag: {e}")
        else:
            logger.warning("cancel_redis not available in context")
        
        result: AnalysisResult = await ai_service.analyze_file_for_strings(
            file_content=file_content,
            file_path=file_path,
            i18n_framework=i18n_framework,
            provider=ai_provider,
            model=ai_model,
            key_naming_style=key_naming_style,
            key_naming_delimiter=key_naming_delimiter,
        )
        
        logger.info(
            f"Analysis complete for {file_path}: "
            f"found {len(result['strings'])} strings, "
            f"used {result['token_usage']['total_tokens']} tokens"
        )
        
        return {
            "file_path": file_path,
            "strings": result["strings"],
            "token_usage": result["token_usage"],
            "scan_session_id": scan_session_id,
            "success": True,
            "error": None,
        }
        
    except Exception as e:
        logger.error(f"Error analyzing {file_path}: {type(e).__name__}: {str(e)}")
        return {
            "file_path": file_path,
            "strings": [],
            "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            "scan_session_id": scan_session_id,
            "success": False,
            "error": str(e),
        }


async def process_pr_file_task(
    ctx: dict,
    file_path: str,
    file_content: str,
    file_sha: Optional[str],
    replacements: list[dict],
    scan_session_id: int,
    translation_function: str,
    ai_provider: str,
    ai_model: str,
    repo_owner: str,
    repo_name: str,
    branch_name: str,
    access_token: str,
) -> dict[str, Any]:
    """
    Process a single file for PR creation - replace hardcoded strings with translation keys.
    
    Args:
        ctx: ARQ context (contains redis connection)
        file_path: Path to the file in the repository
        file_content: Current content of the file
        file_sha: SHA of the file (for GitHub API)
        replacements: List of replacements [{original_text, key, line_number}]
        scan_session_id: ID of the scan session
        translation_function: Name of the translation function (e.g., "t")
        ai_provider: AI provider to use
        ai_model: AI model to use
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        branch_name: Branch to commit to
        access_token: GitHub access token
        
    Returns:
        Dictionary with result:
        - file_path: str
        - success: bool
        - error: optional error message
        - modified: bool (whether the file was actually modified)
    """
    logger.info(f"Processing file for PR: {file_path} with {len(replacements)} replacements")
    
    try:
        # Check Redis cancel flag BEFORE processing
        cancel_redis = ctx.get('cancel_redis')
        if cancel_redis:
            try:
                cancel_key = f"pr_cancelled:{scan_session_id}"
                cancelled = await cancel_redis.get(cancel_key)
                if cancelled:
                    logger.info(f"🛑 PR creation {scan_session_id} was cancelled, skipping file {file_path}")
                    return {
                        "file_path": file_path,
                        "success": False,
                        "error": "PR creation cancelled",
                        "modified": False,
                        "cancelled": True,
                    }
            except Exception as e:
                logger.warning(f"Failed to check cancel flag: {e}")
        
        if not replacements:
            return {
                "file_path": file_path,
                "success": True,
                "error": None,
                "modified": False,
            }
        
        # Use AI to replace strings (understands code context)
        result = await ai_service.replace_strings_in_file(
            file_content=file_content,
            file_path=file_path,
            replacements=replacements,
            translation_function=translation_function,
            provider=ai_provider,
            model=ai_model,
        )
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            logger.error(f"AI replacement failed for {file_path}: {error_msg}")
            return {
                "file_path": file_path,
                "success": False,
                "error": f"AI replacement failed: {error_msg}",
                "modified": False,
            }
        
        new_content = result.get("content", "")
        
        # Only commit if content actually changed
        if not new_content or new_content == file_content:
            logger.info(f"No changes needed for {file_path}")
            return {
                "file_path": file_path,
                "success": True,
                "error": None,
                "modified": False,
            }
        
        # Commit the file to GitHub
        from app.services.github_service import GitHubService
        
        commit_success = await GitHubService.update_file(
            access_token=access_token,
            owner=repo_owner,
            repo=repo_name,
            path=file_path,
            content=new_content,
            message=f"Replace hardcoded strings with translation keys in {file_path.split('/')[-1]}",
            branch=branch_name,
            file_sha=file_sha,
        )
        
        if commit_success:
            logger.info(f"Successfully modified {file_path}")
            return {
                "file_path": file_path,
                "success": True,
                "error": None,
                "modified": True,
            }
        else:
            logger.error(f"Failed to commit {file_path}")
            return {
                "file_path": file_path,
                "success": False,
                "error": "Failed to commit file to GitHub",
                "modified": False,
            }
        
    except Exception as e:
        logger.error(f"Error processing {file_path} for PR: {type(e).__name__}: {str(e)}")
        return {
            "file_path": file_path,
            "success": False,
            "error": str(e),
            "modified": False,
        }


async def startup(ctx: dict) -> None:
    """Called when worker starts."""
    # Create dedicated Redis client for cancel checks
    redis_settings = get_redis_settings()
    ctx['cancel_redis'] = Redis(
        host=redis_settings.host,
        port=redis_settings.port,
        password=redis_settings.password,
        db=redis_settings.database,
        decode_responses=True,
    )
    logger.info("Scanner worker started with cancel check Redis")


async def shutdown(ctx: dict) -> None:
    """Called when worker shuts down."""
    # Close Redis client
    if 'cancel_redis' in ctx:
        await ctx['cancel_redis'].close()
    logger.info("Scanner worker shutting down")


class WorkerSettings:
    """ARQ Worker settings."""
    
    functions = [analyze_file_task, process_pr_file_task]
    on_startup = startup
    on_shutdown = shutdown
    
    redis_settings = get_redis_settings()
    
    # Worker configuration
    max_jobs = settings.scanner_max_concurrent_jobs
    job_timeout = settings.scanner_job_timeout
    
    # Retry configuration
    max_tries = 2
    retry_delay = 5  # seconds


# Helper function to create redis pool for enqueueing jobs
async def get_redis_pool() -> Redis:
    """Get Redis connection pool for enqueueing jobs."""
    redis_settings = get_redis_settings()
    return await create_pool(redis_settings)


if __name__ == "__main__":
    # For testing: run worker directly
    from arq import run_worker
    run_worker(WorkerSettings)

