from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class ProjectAccess(Base):
    """
    Project access model for managing user access to specific projects within a team.
    Defines granular access control at the project level.
    Roles: admin, editor, viewer, translator, reviewer
    """
    __tablename__ = "project_access"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), default="viewer", nullable=False)  # admin, editor, viewer, translator, reviewer
    granted_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="access_members")
    user = relationship("User", foreign_keys=[user_id], back_populates="project_access")
    granted_by = relationship("User", foreign_keys=[granted_by_user_id])

