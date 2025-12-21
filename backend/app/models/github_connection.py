"""
GitHub Connection model for storing OAuth tokens.
Connects GitHub accounts to Teams for repository access.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base


class GitHubConnection(Base):
    """
    GitHub OAuth connection model.
    Stores encrypted access tokens for GitHub API access.
    
    A GitHub connection is linked to a Team, allowing all team members
    to use it for repository operations. The actual GitHub account
    belongs to the user who connected it (connected_by_user_id).
    """
    __tablename__ = "github_connections"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4, nullable=False)
    
    # Team relationship - GitHub account belongs to team
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # User who connected this account (for audit)
    connected_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # GitHub OAuth data
    access_token = Column(Text, nullable=False)  # Encrypted token
    refresh_token = Column(Text, nullable=True)  # Encrypted refresh token (for expiring tokens)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)  # When access_token expires
    token_type = Column(String(50), default="bearer")
    scope = Column(String(500))  # Granted scopes
    
    # GitHub user info
    github_user_id = Column(String(50), nullable=False, index=True)
    github_username = Column(String(255), nullable=False)
    github_avatar_url = Column(String(500))
    github_email = Column(String(255))
    
    # Timestamps
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="github_connections")
    connected_by = relationship("User", back_populates="connected_github_accounts")
    repositories = relationship("Repository", back_populates="github_connection")
    
    def __repr__(self) -> str:
        return f"<GitHubConnection(id={self.id}, team_id={self.team_id}, github_username={self.github_username})>"
