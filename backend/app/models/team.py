from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base


class Team(Base):
    """
    Team model for managing groups of users working together.
    Uses UUID for public identification to prevent enumeration attacks.
    """
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)  # Internal use only
    public_id = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="owned_teams")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    invitations = relationship("TeamInvitation", back_populates="team", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="team")
    github_connections = relationship("GitHubConnection", back_populates="team", cascade="all, delete-orphan")
    token_usages = relationship("TokenUsage", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    """
    Team member model for managing team access.
    Defines who has access to a team and their role.
    Roles: admin, editor, viewer, translator, reviewer
    """
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), default="viewer", nullable=False)  # admin, editor, viewer, translator, reviewer
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")

