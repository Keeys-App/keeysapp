from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import bcrypt as bcrypt_lib
from app.models.base import Base


def _truncate_password_bytes(password: str) -> bytes:
    """
    Convert password to bytes and truncate to maximum bcrypt length (72 bytes).
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return password_bytes


class User(Base):
    """
    User model for authentication and authorization.
    Uses UUID for public identification to prevent enumeration attacks.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # Internal use only
    public_id = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4, nullable=False)  # Public facing ID
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    onboarding_completed = Column(Boolean, default=False, nullable=False)  # Track onboarding status
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owned_projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    owned_teams = relationship("Team", back_populates="owner", cascade="all, delete-orphan")
    team_memberships = relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")
    project_access = relationship("ProjectAccess", foreign_keys="[ProjectAccess.user_id]", back_populates="user", cascade="all, delete-orphan")
    # Legacy relationship kept for compatibility during migration
    project_memberships = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")

    def verify_password(self, plain_password: str) -> bool:
        """
        Verify a plain password against the hashed password.
        
        Args:
            plain_password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        password_bytes = _truncate_password_bytes(plain_password)
        return bcrypt_lib.checkpw(password_bytes, self.hashed_password.encode('utf-8'))

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Hash a password for storing.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password as string
        """
        password_bytes = _truncate_password_bytes(password)
        hashed = bcrypt_lib.hashpw(password_bytes, bcrypt_lib.gensalt())
        return hashed.decode('utf-8')

