from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum


class KeyActionType(str, enum.Enum):
    """Enum for different types of key actions that can be logged"""
    CREATE = "CREATE"
    UPDATE_KEY = "UPDATE_KEY"
    UPDATE_DESCRIPTION = "UPDATE_DESCRIPTION"
    UPDATE_TRANSLATION = "UPDATE_TRANSLATION"
    DELETE_TRANSLATION = "DELETE_TRANSLATION"
    DELETE = "DELETE"
    IMPORT = "IMPORT"


class KeyLog(Base):
    """
    Audit log for tracking all changes to translation keys.
    Records who changed what, when, and from what to what value.
    Does not log metadata changes (tags, etc).
    """
    __tablename__ = "key_logs"

    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(Integer, ForeignKey("keys.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(SQLEnum(KeyActionType), nullable=False, index=True)
    
    # Field information
    field_name = Column(String(100), nullable=True)  # e.g., "key", "description", "translation"
    language = Column(String(10), nullable=True)  # Only for translation changes
    
    # Change tracking
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    key = relationship("Key", backref="logs")
    user = relationship("User", backref="key_logs")

