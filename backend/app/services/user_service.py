from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from uuid import UUID
from app.models.user import User


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
    def search_users(db: Session, query: str, limit: int = 10) -> List[User]:
        """
        Search users by email or username.
        Case-insensitive search.
        
        Args:
            db: Database session
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching users
        """
        if not query or len(query) < 2:
            return []
        
        search_pattern = f"%{query.lower()}%"
        
        return db.query(User).filter(
            User.is_active == True,
            or_(
                func.lower(User.email).like(search_pattern),
                func.lower(User.username).like(search_pattern)
            )
        ).limit(limit).all()

