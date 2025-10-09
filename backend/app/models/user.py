from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
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
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

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

