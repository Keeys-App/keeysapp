from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base


class Key(Base):
    """
    Key model for managing translation keys within a project.
    Each key belongs to a project and has multiple translations in different languages.
    """
    __tablename__ = "keys"

    id = Column(Integer, primary_key=True, index=True)  # Internal use only
    public_id = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4, nullable=False)
    key = Column(String(500), nullable=False)  # Translation key, e.g., "button.submit"
    description = Column(Text, nullable=True)  # Optional description for translators
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="keys")
    translations = relationship("Translation", back_populates="key", cascade="all, delete-orphan")

    # Ensure key uniqueness within a project
    __table_args__ = (
        UniqueConstraint('project_id', 'key', name='uq_project_key'),
    )


class Translation(Base):
    """
    Translation model for storing translations of keys in different languages.
    Each translation is for a specific key and language combination.
    """
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, index=True)
    key_id = Column(Integer, ForeignKey("keys.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(10), nullable=False)  # Language code, e.g., "en", "ru", "de"
    value = Column(Text, nullable=False)  # Translated text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    key = relationship("Key", back_populates="translations")

    # Ensure one translation per language per key
    __table_args__ = (
        UniqueConstraint('key_id', 'language', name='uq_key_language'),
    )

