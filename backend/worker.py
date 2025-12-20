"""
ARQ Worker for background file analysis tasks.

Run with: arq worker.WorkerSettings
"""
import asyncio
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
        result: AnalysisResult = await ai_service.analyze_file_for_strings(
            file_content=file_content,
            file_path=file_path,
            i18n_framework=i18n_framework,
            provider=ai_provider,
            model=ai_model,
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


async def startup(ctx: dict) -> None:
    """Called when worker starts."""
    logger.info("Scanner worker started")


async def shutdown(ctx: dict) -> None:
    """Called when worker shuts down."""
    logger.info("Scanner worker shutting down")


class WorkerSettings:
    """ARQ Worker settings."""
    
    functions = [analyze_file_task]
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

