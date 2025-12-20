"""
Repository model for linking GitHub repositories to projects.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base


class Repository(Base):
    """
    GitHub Repository model.
    Links a GitHub repository to a Keeys project for localization.
    
    A repository is connected to:
    - A Project (for localization)
    - A GitHubConnection (for API access)
    """
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4, nullable=False)
    
    # Project relationship - which project this repo is linked to
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # GitHub connection to use for API access
    github_connection_id = Column(Integer, ForeignKey("github_connections.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Repository info from GitHub
    github_repo_id = Column(String(50), nullable=False)  # GitHub repository ID
    repo_owner = Column(String(255), nullable=False)  # e.g., "myorg"
    repo_name = Column(String(255), nullable=False)   # e.g., "frontend-app"
    default_branch = Column(String(255), default="main")
    
    # i18n Configuration
    i18n_framework = Column(String(50))  # react-i18next, vue-i18n, etc.
    source_patterns = Column(JSON, default=list)  # ["src/**/*.tsx", "src/**/*.vue"]
    locale_path = Column(String(500))  # Path to locale files, e.g., "src/locales"
    
    # Timestamps
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="repositories")
    github_connection = relationship("GitHubConnection", back_populates="repositories")
    
    def __repr__(self) -> str:
        return f"<Repository(id={self.id}, repo={self.repo_owner}/{self.repo_name}, project_id={self.project_id})>"
    
    @property
    def full_name(self) -> str:
        """Get full repository name (owner/repo)."""
        return f"{self.repo_owner}/{self.repo_name}"

