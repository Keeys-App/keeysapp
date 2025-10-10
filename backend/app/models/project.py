from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base


class Project(Base):
    """
    Project model for managing localization projects.
    Uses UUID for public identification to prevent enumeration attacks.
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)  # Internal use only
    public_id = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    languages = Column(JSON, default=list, nullable=False)  # Array of language objects: [{"code": "en", "locale": "en-US"}, ...]
    default_language = Column(String(10), nullable=True)  # Default language code (must be in languages array)
    available_tags = Column(JSON, default=list, nullable=False)  # Array of tag strings available in project
    color = Column(String(7), default="#6366f1", nullable=False)  # Hex color code
    status = Column(String(20), default="active", nullable=False)  # active, archived, draft
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="owned_projects")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    keys = relationship("Key", back_populates="project", cascade="all, delete-orphan")


class ProjectMember(Base):
    """
    Project member model for managing project access.
    Defines who has access to a project and their role.
    """
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), default="viewer", nullable=False)  # admin, editor, viewer
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")

