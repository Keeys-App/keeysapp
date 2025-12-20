"""
TokenUsage model for tracking AI API token consumption.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.models.base import Base
from app.models.scan_session import AIProvider


class OperationType(str, enum.Enum):
    """Enum for AI operation types."""
    SCAN_FILE = "SCAN_FILE"      # Scanning file for strings
    TRANSLATE = "TRANSLATE"      # Translating text
    REPHRASE = "REPHRASE"        # Rephrasing text
    SHORTEN = "SHORTEN"          # Shortening text
    VARIANTS = "VARIANTS"        # Generating variants


class TokenUsage(Base):
    """
    TokenUsage model for tracking AI API token consumption.
    Records every AI API call with input/output token counts.
    """
    __tablename__ = "token_usages"

    id = Column(Integer, primary_key=True, index=True)
    
    # Team for billing (required)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # User who initiated the operation (optional)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Operation details
    operation_type = Column(SQLEnum(OperationType), nullable=False, index=True)
    provider = Column(SQLEnum(AIProvider), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    
    # Token counts
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    
    # Optional link to scan session (for SCAN_FILE operations)
    scan_session_id = Column(Integer, ForeignKey("scan_sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    team = relationship("Team", back_populates="token_usages")
    user = relationship("User", back_populates="token_usages")
    scan_session = relationship("ScanSession", back_populates="token_usages")

    def __repr__(self) -> str:
        return f"<TokenUsage(id={self.id}, operation={self.operation_type}, tokens={self.total_tokens})>"

