"""
FoundString model for storing strings found during repository scanning.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.models.base import Base


class FoundStringStatus(str, enum.Enum):
    """Enum for found string status."""
    PENDING = "PENDING"      # Waiting for review
    APPROVED = "APPROVED"    # Approved for conversion
    SKIPPED = "SKIPPED"      # Skipped by user
    CONVERTED = "CONVERTED"  # Converted to a project key


class FoundString(Base):
    """
    FoundString model for storing strings found during repository scanning.
    Each found string is a potential translation key discovered by AI analysis.
    """
    __tablename__ = "found_strings"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4, nullable=False)
    
    # Scan session relationship
    scan_session_id = Column(Integer, ForeignKey("scan_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # File location
    file_path = Column(String(1000), nullable=False)  # Path in repository
    line_number = Column(Integer, nullable=True)       # Line number in file
    
    # String content
    original_text = Column(Text, nullable=False)       # The hardcoded string found
    suggested_key = Column(String(500), nullable=False)  # AI-suggested key name
    context = Column(Text, nullable=True)              # AI explanation of context
    
    # AI confidence score (0.0 to 1.0)
    confidence = Column(Integer, default=100, nullable=False)  # Stored as 0-100 for simplicity
    
    # Status
    status = Column(SQLEnum(FoundStringStatus), nullable=False, default=FoundStringStatus.PENDING, server_default="PENDING")
    
    # Link to created key (after conversion)
    key_id = Column(Integer, ForeignKey("keys.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    scan_session = relationship("ScanSession", back_populates="found_strings")
    key = relationship("Key", back_populates="found_strings")

    def __repr__(self) -> str:
        return f"<FoundString(id={self.id}, key={self.suggested_key}, status={self.status})>"

