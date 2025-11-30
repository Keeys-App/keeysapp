from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum


class ActionType(str, enum.Enum):
    """Enum for all types of actions that can be logged in the system"""
    
    # Project lifecycle actions
    PROJECT_CREATE = "PROJECT_CREATE"
    PROJECT_UPDATE_NAME = "PROJECT_UPDATE_NAME"
    PROJECT_UPDATE_DESCRIPTION = "PROJECT_UPDATE_DESCRIPTION"
    PROJECT_UPDATE_LANGUAGES = "PROJECT_UPDATE_LANGUAGES"
    PROJECT_UPDATE_DEFAULT_LANGUAGE = "PROJECT_UPDATE_DEFAULT_LANGUAGE"
    PROJECT_UPDATE_COLOR = "PROJECT_UPDATE_COLOR"
    PROJECT_UPDATE_STATUS = "PROJECT_UPDATE_STATUS"
    PROJECT_DELETE = "PROJECT_DELETE"
    PROJECT_EXPORT = "PROJECT_EXPORT"
    PROJECT_IMPORT = "PROJECT_IMPORT"
    
    # Team lifecycle actions
    TEAM_CREATE = "TEAM_CREATE"
    TEAM_UPDATE_NAME = "TEAM_UPDATE_NAME"
    TEAM_UPDATE_DESCRIPTION = "TEAM_UPDATE_DESCRIPTION"
    TEAM_DELETE = "TEAM_DELETE"
    
    # Team management actions
    MEMBER_ADD = "MEMBER_ADD"
    MEMBER_REMOVE = "MEMBER_REMOVE"
    MEMBER_ROLE_CHANGE = "MEMBER_ROLE_CHANGE"
    TEAM_INVITE = "TEAM_INVITE"
    
    # Key actions
    KEY_CREATE = "KEY_CREATE"
    KEY_UPDATE = "KEY_UPDATE"
    KEY_UPDATE_DESCRIPTION = "KEY_UPDATE_DESCRIPTION"
    KEY_DELETE = "KEY_DELETE"
    
    # Translation actions
    TRANSLATION_UPDATE = "TRANSLATION_UPDATE"
    TRANSLATION_AI_UPDATE = "TRANSLATION_AI_UPDATE"
    TRANSLATION_DELETE = "TRANSLATION_DELETE"
    TRANSLATION_IMPORT = "TRANSLATION_IMPORT"
    
    # Review actions
    REVIEW_APPROVE = "REVIEW_APPROVE"
    REVIEW_REJECT = "REVIEW_REJECT"
    REVIEW_DELETE = "REVIEW_DELETE"


class ActivityLog(Base):
    """
    Universal audit log for tracking all changes in the system.
    Records project-level actions, key changes, translations, and team management.
    Uses SET NULL for foreign keys to preserve history even after entity deletion.
    """
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Entity references (nullable to preserve history after deletion)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    key_id = Column(Integer, ForeignKey("keys.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # User who performed the action
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # For team management - affected user (who was added/removed/changed)
    affected_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Action details
    action = Column(SQLEnum(ActionType), nullable=False, index=True)
    field_name = Column(String(100), nullable=True)  # e.g., "name", "description", "translation"
    language = Column(String(10), nullable=True)  # Only for translation-related actions
    
    # Change tracking
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)  # For review actions: stores comment
    
    # Optional extra data for complex actions (JSON)
    extra_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    team = relationship("Team", backref="activity_logs")
    project = relationship("Project", backref="activity_logs")
    key = relationship("Key", backref="activity_logs")
    user = relationship("User", backref="activity_logs_performed", foreign_keys=[user_id])
    affected_user = relationship("User", backref="activity_logs_affected", foreign_keys=[affected_user_id])

