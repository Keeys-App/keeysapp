"""
Password reset token model for secure password recovery.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import secrets
from datetime import datetime, timedelta, timezone

from app.models.base import Base


class PasswordResetToken(Base):
    """
    Token for password reset functionality.
    Tokens are single-use and expire after a set time.
    """
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)

    # Relationship
    user = relationship("User", backref="password_reset_tokens")

    @staticmethod
    def generate_token() -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_expiration(hours: int = 1) -> datetime:
        """Create expiration datetime."""
        return datetime.now(timezone.utc) + timedelta(hours=hours)

    @property
    def is_valid(self) -> bool:
        """Check if token is still valid (not used and not expired)."""
        if self.used:
            return False
        now = datetime.now(timezone.utc)
        # Handle timezone-aware and naive datetimes
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return now < expires_at

