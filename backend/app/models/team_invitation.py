from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.models.base import Base


class InvitationStatus(str, enum.Enum):
    """Status of team invitation."""
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"


class TeamInvitation(Base):
    """
    Team invitation model for inviting users to teams.
    Supports inviting both existing and non-existing users.
    """
    __tablename__ = "team_invitations"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    invited_email = Column(String, nullable=False)  # Email of invited user (may not exist yet)
    role = Column(String(20), default="viewer", nullable=False)  # admin, editor, viewer, translator, reviewer
    status = Column(SQLEnum(InvitationStatus), default=InvitationStatus.PENDING, nullable=False)
    invited_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    invited_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # Set if user exists
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    team = relationship("Team", back_populates="invitations")
    invited_by = relationship("User", foreign_keys=[invited_by_user_id])
    invited_user = relationship("User", foreign_keys=[invited_user_id])

