"""
Token Usage Service for tracking AI API token consumption.
"""
import logging
from typing import Optional, TypedDict
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.token_usage import TokenUsage, OperationType
from app.models.scan_session import AIProvider

logger = logging.getLogger(__name__)


class TokenUsageStats(TypedDict):
    """Type definition for token usage statistics."""
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    operations_count: int
    by_operation: dict[str, int]
    by_provider: dict[str, int]
    by_model: dict[str, int]


class TokenUsageService:
    """Service for tracking and querying AI token usage."""
    
    @staticmethod
    async def record_usage(
        db: AsyncSession,
        team_id: int,
        operation_type: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        user_id: Optional[int] = None,
        scan_session_id: Optional[int] = None,
    ) -> TokenUsage:
        """
        Record token usage for an AI operation.
        
        Args:
            db: Database session
            team_id: Team ID for billing
            operation_type: Type of operation (SCAN_FILE, TRANSLATE, etc.)
            provider: AI provider (OPENAI, ANTHROPIC)
            model: Model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            user_id: Optional user ID who initiated
            scan_session_id: Optional scan session ID
            
        Returns:
            Created TokenUsage record
        """
        try:
            # Parse operation type
            op_type = OperationType(operation_type.upper())
        except ValueError:
            op_type = OperationType.SCAN_FILE
        
        try:
            # Parse provider
            ai_provider = AIProvider(provider.upper())
        except ValueError:
            ai_provider = AIProvider.ANTHROPIC
        
        total_tokens = input_tokens + output_tokens
        
        usage = TokenUsage(
            team_id=team_id,
            user_id=user_id,
            operation_type=op_type,
            provider=ai_provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            scan_session_id=scan_session_id,
        )
        
        db.add(usage)
        await db.commit()
        await db.refresh(usage)
        
        logger.debug(f"Recorded token usage: {total_tokens} tokens for {operation_type}")
        return usage
    
    @staticmethod
    async def get_team_usage(
        db: AsyncSession,
        team_id: int,
        days: int = 30,
    ) -> TokenUsageStats:
        """
        Get token usage statistics for a team.
        
        Args:
            db: Database session
            team_id: Team ID
            days: Number of days to look back (default: 30)
            
        Returns:
            Token usage statistics
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        # Get totals
        result = await db.execute(
            select(
                func.sum(TokenUsage.input_tokens).label("total_input"),
                func.sum(TokenUsage.output_tokens).label("total_output"),
                func.sum(TokenUsage.total_tokens).label("total"),
                func.count(TokenUsage.id).label("count"),
            )
            .where(
                TokenUsage.team_id == team_id,
                TokenUsage.created_at >= since,
            )
        )
        row = result.fetchone()
        
        total_input = row.total_input or 0
        total_output = row.total_output or 0
        total = row.total or 0
        count = row.count or 0
        
        # Get breakdown by operation type
        result = await db.execute(
            select(
                TokenUsage.operation_type,
                func.sum(TokenUsage.total_tokens).label("tokens"),
            )
            .where(
                TokenUsage.team_id == team_id,
                TokenUsage.created_at >= since,
            )
            .group_by(TokenUsage.operation_type)
        )
        by_operation = {row.operation_type.value: row.tokens or 0 for row in result.fetchall()}
        
        # Get breakdown by provider
        result = await db.execute(
            select(
                TokenUsage.provider,
                func.sum(TokenUsage.total_tokens).label("tokens"),
            )
            .where(
                TokenUsage.team_id == team_id,
                TokenUsage.created_at >= since,
            )
            .group_by(TokenUsage.provider)
        )
        by_provider = {row.provider.value: row.tokens or 0 for row in result.fetchall()}
        
        # Get breakdown by model
        result = await db.execute(
            select(
                TokenUsage.model,
                func.sum(TokenUsage.total_tokens).label("tokens"),
            )
            .where(
                TokenUsage.team_id == team_id,
                TokenUsage.created_at >= since,
            )
            .group_by(TokenUsage.model)
        )
        by_model = {row.model: row.tokens or 0 for row in result.fetchall()}
        
        return TokenUsageStats(
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            total_tokens=total,
            operations_count=count,
            by_operation=by_operation,
            by_provider=by_provider,
            by_model=by_model,
        )
    
    @staticmethod
    async def get_scan_usage(
        db: AsyncSession,
        scan_session_id: int,
    ) -> TokenUsageStats:
        """
        Get token usage for a specific scan session.
        
        Args:
            db: Database session
            scan_session_id: Scan session ID
            
        Returns:
            Token usage statistics for the scan
        """
        # Get totals
        result = await db.execute(
            select(
                func.sum(TokenUsage.input_tokens).label("total_input"),
                func.sum(TokenUsage.output_tokens).label("total_output"),
                func.sum(TokenUsage.total_tokens).label("total"),
                func.count(TokenUsage.id).label("count"),
            )
            .where(TokenUsage.scan_session_id == scan_session_id)
        )
        row = result.fetchone()
        
        total_input = row.total_input or 0
        total_output = row.total_output or 0
        total = row.total or 0
        count = row.count or 0
        
        # Get breakdown by model
        result = await db.execute(
            select(
                TokenUsage.model,
                func.sum(TokenUsage.total_tokens).label("tokens"),
            )
            .where(TokenUsage.scan_session_id == scan_session_id)
            .group_by(TokenUsage.model)
        )
        by_model = {row.model: row.tokens or 0 for row in result.fetchall()}
        
        # Get breakdown by provider
        result = await db.execute(
            select(
                TokenUsage.provider,
                func.sum(TokenUsage.total_tokens).label("tokens"),
            )
            .where(TokenUsage.scan_session_id == scan_session_id)
            .group_by(TokenUsage.provider)
        )
        by_provider = {row.provider.value: row.tokens or 0 for row in result.fetchall()}
        
        return TokenUsageStats(
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            total_tokens=total,
            operations_count=count,
            by_operation={"SCAN_FILE": total},
            by_provider=by_provider,
            by_model=by_model,
        )
    
    @staticmethod
    async def get_user_usage(
        db: AsyncSession,
        user_id: int,
        days: int = 30,
    ) -> TokenUsageStats:
        """
        Get token usage statistics for a user.
        
        Args:
            db: Database session
            user_id: User ID
            days: Number of days to look back (default: 30)
            
        Returns:
            Token usage statistics
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        # Get totals
        result = await db.execute(
            select(
                func.sum(TokenUsage.input_tokens).label("total_input"),
                func.sum(TokenUsage.output_tokens).label("total_output"),
                func.sum(TokenUsage.total_tokens).label("total"),
                func.count(TokenUsage.id).label("count"),
            )
            .where(
                TokenUsage.user_id == user_id,
                TokenUsage.created_at >= since,
            )
        )
        row = result.fetchone()
        
        total_input = row.total_input or 0
        total_output = row.total_output or 0
        total = row.total or 0
        count = row.count or 0
        
        # Get breakdown by operation type
        result = await db.execute(
            select(
                TokenUsage.operation_type,
                func.sum(TokenUsage.total_tokens).label("tokens"),
            )
            .where(
                TokenUsage.user_id == user_id,
                TokenUsage.created_at >= since,
            )
            .group_by(TokenUsage.operation_type)
        )
        by_operation = {row.operation_type.value: row.tokens or 0 for row in result.fetchall()}
        
        # Get breakdown by provider
        result = await db.execute(
            select(
                TokenUsage.provider,
                func.sum(TokenUsage.total_tokens).label("tokens"),
            )
            .where(
                TokenUsage.user_id == user_id,
                TokenUsage.created_at >= since,
            )
            .group_by(TokenUsage.provider)
        )
        by_provider = {row.provider.value: row.tokens or 0 for row in result.fetchall()}
        
        # Get breakdown by model
        result = await db.execute(
            select(
                TokenUsage.model,
                func.sum(TokenUsage.total_tokens).label("tokens"),
            )
            .where(
                TokenUsage.user_id == user_id,
                TokenUsage.created_at >= since,
            )
            .group_by(TokenUsage.model)
        )
        by_model = {row.model: row.tokens or 0 for row in result.fetchall()}
        
        return TokenUsageStats(
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            total_tokens=total,
            operations_count=count,
            by_operation=by_operation,
            by_provider=by_provider,
            by_model=by_model,
        )

