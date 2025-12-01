from typing import Optional
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken

logger = logging.getLogger(__name__)


class UserService:
    """
    Service for user-related operations.
    """

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User object or None
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            db: Database session
            username: Username
            
        Returns:
            User object or None
        """
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Get user by internal ID.
        For internal use only. Use get_user_by_public_id for public API.
        
        Args:
            db: Database session
            user_id: Internal user ID
            
        Returns:
            User object or None
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_public_id(db: Session, public_id: str) -> Optional[User]:
        """
        Get user by public UUID.
        Use this method for public-facing APIs to prevent enumeration attacks.
        
        Args:
            db: Database session
            public_id: User's public UUID (as string)
            
        Returns:
            User object or None
        """
        try:
            uuid_obj = UUID(public_id)
            return db.query(User).filter(User.public_id == uuid_obj).first()
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def create_user(db: Session, email: str, username: str, password: str) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            email: User email
            username: Username
            password: Plain text password
            
        Returns:
            Created user object
        """
        hashed_password = User.get_password_hash(password)
        db_user = User(
            email=email,
            username=username,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not user.verify_password(password):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    def create_password_reset_token(db: Session, user: User) -> PasswordResetToken:
        """
        Create a password reset token for a user.
        Invalidates any existing unused tokens for the user.
        
        Args:
            db: Database session
            user: User object
            
        Returns:
            PasswordResetToken object
        """
        # Invalidate existing unused tokens
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False
        ).update({"used": True})
        
        # Create new token
        token = PasswordResetToken(
            token=PasswordResetToken.generate_token(),
            user_id=user.id,
            expires_at=PasswordResetToken.create_expiration(hours=1)
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        
        logger.info(f"Created password reset token for user {user.email}")
        return token

    @staticmethod
    def get_password_reset_token(db: Session, token: str) -> Optional[PasswordResetToken]:
        """
        Get a password reset token by token string.
        
        Args:
            db: Database session
            token: Token string
            
        Returns:
            PasswordResetToken object or None
        """
        return db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token
        ).first()

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        """
        Reset user password using a valid token.
        
        Args:
            db: Database session
            token: Password reset token string
            new_password: New password to set
            
        Returns:
            True if password was reset successfully, False otherwise
        """
        reset_token = UserService.get_password_reset_token(db, token)
        
        if not reset_token:
            logger.warning(f"Password reset attempt with invalid token")
            return False
        
        if not reset_token.is_valid:
            logger.warning(f"Password reset attempt with expired/used token for user_id {reset_token.user_id}")
            return False
        
        # Get the user
        user = UserService.get_user_by_id(db, reset_token.user_id)
        if not user:
            logger.error(f"User not found for password reset token")
            return False
        
        # Update password - use explicit update to ensure change is tracked
        new_hash = User.get_password_hash(new_password)
        db.query(User).filter(User.id == user.id).update(
            {"hashed_password": new_hash}
        )
        
        # Mark token as used
        reset_token.used = True
        
        db.commit()
        logger.info(f"Password reset successful for user {user.email}")
        return True

    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """
        Remove expired password reset tokens.
        
        Args:
            db: Database session
            
        Returns:
            Number of tokens removed
        """
        now = datetime.now(timezone.utc)
        result = db.query(PasswordResetToken).filter(
            PasswordResetToken.expires_at < now
        ).delete()
        db.commit()
        logger.info(f"Cleaned up {result} expired password reset tokens")
        return result

    @staticmethod
    def update_profile(
        db: Session,
        user: User,
        username: Optional[str] = None,
        email: Optional[str] = None
    ) -> User:
        """
        Update user profile.
        
        Args:
            db: Database session
            user: User to update
            username: New username (optional)
            email: New email (optional)
            
        Returns:
            Updated user object
        """
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        
        db.commit()
        db.refresh(user)
        logger.info(f"Profile updated for user {user.email}")
        return user

    @staticmethod
    def change_password(
        db: Session,
        user: User,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password after verifying current password.
        
        Args:
            db: Database session
            user: User to update
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            True if password was changed successfully, False otherwise
        """
        if not user.verify_password(current_password):
            return False
        
        new_hash = User.get_password_hash(new_password)
        db.query(User).filter(User.id == user.id).update(
            {"hashed_password": new_hash}
        )
        db.commit()
        logger.info(f"Password changed for user {user.email}")
        return True

