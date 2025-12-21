"""
ScanSession model for tracking repository scanning operations.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

from app.models.base import Base


class ScanStatus(str, enum.Enum):
    """Enum for scan session status."""
    PENDING = "PENDING"
    SCANNING = "SCANNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AIProvider(str, enum.Enum):
    """Enum for AI provider."""
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"


class ScanSession(Base):
    """
    ScanSession model for tracking repository scanning operations.
    Each scan session belongs to a repository and tracks the progress
    of scanning files for hardcoded strings.
    """
    __tablename__ = "scan_sessions"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4, nullable=False)
    
    # Repository relationship
    repository_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # User who started the scan
    started_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Scan status
    status = Column(SQLEnum(ScanStatus), nullable=False, default=ScanStatus.PENDING, server_default="PENDING")
    
    # AI configuration
    ai_provider = Column(SQLEnum(AIProvider), nullable=False, default=AIProvider.ANTHROPIC)
    ai_model = Column(String(100), nullable=False, default="claude-haiku-4-5")
    
    # Key naming configuration
    key_naming_style = Column(String(20), nullable=True, default="camelCase")  # UPPERCASE, snake_case, camelCase
    key_naming_delimiter = Column(String(5), nullable=True, default=".")  # _, ., :, ::
    
    # Scan path (optional directory to limit scan scope)
    scan_path = Column(String(500), nullable=True)
    
    # Progress tracking
    files_total = Column(Integer, default=0, nullable=False)
    files_scanned = Column(Integer, default=0, nullable=False)
    strings_found = Column(Integer, default=0, nullable=False)
    
    # List of processed file paths (for resume after restart)
    processed_files = Column(JSONB, default=list, nullable=False, server_default='[]')
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Pull Request information
    pr_branch_name = Column(String(255), nullable=True)
    pr_number = Column(Integer, nullable=True)
    pr_url = Column(String(500), nullable=True)
    pr_created_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    repository = relationship("Repository", back_populates="scan_sessions")
    started_by_user = relationship("User", back_populates="scan_sessions")
    found_strings = relationship("FoundString", back_populates="scan_session", cascade="all, delete-orphan")
    token_usages = relationship("TokenUsage", back_populates="scan_session")

    def __repr__(self) -> str:
        return f"<ScanSession(id={self.id}, repository_id={self.repository_id}, status={self.status})>"

