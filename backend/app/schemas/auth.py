import strawberry
from typing import Optional, List
from datetime import timedelta
from strawberry.types import Info
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
import logging

from app.database import get_db
from app.services.user_service import UserService
from app.core.security import create_access_token, decode_access_token
from app.core.exceptions import (
    AuthenticationError,
    UnauthorizedError,
    UserAlreadyExistsError,
    ValidationError,
    DatabaseError,
    handle_database_exception
)


import uuid as uuid_lib

logger = logging.getLogger(__name__)


@strawberry.type
class UserType:
    """
    GraphQL type for User.
    Uses public_id (UUID) instead of internal ID for security.
    """
    id: str  # UUID as string for public API
    email: str
    username: str
    is_active: bool
    is_superuser: bool


@strawberry.type
class AuthPayload:
    """
    GraphQL type for authentication response.
    """
    access_token: str
    token_type: str
    user: UserType


@strawberry.input
class RegisterInput:
    """
    Input type for user registration.
    """
    email: str
    username: str
    password: str


@strawberry.input
class LoginInput:
    """
    Input type for user login.
    """
    email: str
    password: str


@strawberry.type
class AuthMutation:
    """
    GraphQL mutations for authentication.
    """

    @strawberry.mutation
    def register(self, input: RegisterInput, info: Info) -> AuthPayload:
        """
        Register a new user.
        
        Args:
            input: Registration input data
            info: GraphQL info object
            
        Returns:
            AuthPayload with access token and user data
            
        Raises:
            ValidationError: If password is too short or too long
            UserAlreadyExistsError: If email or username already exists
            DatabaseError: If database operation fails
        """
        db: Session = next(get_db())
        
        try:
            # Validate password
            if len(input.password) < 8:
                raise ValidationError("Password must be at least 8 characters long")
            if len(input.password) > 72:
                raise ValidationError("Password must be no more than 72 characters long")
            
            # Check if email already exists
            existing_user = UserService.get_user_by_email(db, input.email)
            if existing_user:
                raise UserAlreadyExistsError(field="email")
            
            # Check if username already exists
            existing_username = UserService.get_user_by_username(db, input.username)
            if existing_username:
                raise UserAlreadyExistsError(field="username")
            
            # Create user
            user = UserService.create_user(
                db=db,
                email=input.email,
                username=input.username,
                password=input.password
            )
            
            # Create access token using public_id (UUID) for security
            access_token = create_access_token(data={"sub": str(user.public_id)})
            
            return AuthPayload(
                access_token=access_token,
                token_type="bearer",
                user=UserType(
                    id=str(user.public_id),  # Use UUID for public API
                    email=user.email,
                    username=user.username,
                    is_active=user.is_active,
                    is_superuser=user.is_superuser
                )
            )
        except (UserAlreadyExistsError, AuthenticationError, ValidationError):
            # Re-raise app exceptions as-is (they have safe messages)
            raise
        except (IntegrityError, OperationalError) as e:
            # Database errors - never expose to users!
            handle_database_exception(e, "user registration")
        except Exception as e:
            # Catch-all for unexpected errors
            handle_database_exception(e, "user registration")
        finally:
            db.close()

    @strawberry.mutation
    def login(self, input: LoginInput, info: Info) -> AuthPayload:
        """
        Authenticate a user.
        
        Args:
            input: Login input data
            info: GraphQL info object
            
        Returns:
            AuthPayload with access token and user data
            
        Raises:
            AuthenticationError: If authentication fails
            DatabaseError: If database operation fails
        """
        db: Session = next(get_db())
        
        try:
            # Authenticate user
            user = UserService.authenticate_user(db, input.email, input.password)
            if not user:
                raise AuthenticationError()
            
            # Create access token using public_id (UUID) for security
            access_token = create_access_token(data={"sub": str(user.public_id)})
            
            return AuthPayload(
                access_token=access_token,
                token_type="bearer",
                user=UserType(
                    id=str(user.public_id),  # Use UUID for public API
                    email=user.email,
                    username=user.username,
                    is_active=user.is_active,
                    is_superuser=user.is_superuser
                )
            )
        except (AuthenticationError, UserAlreadyExistsError):
            # Re-raise app exceptions as-is (they have safe messages)
            raise
        except (IntegrityError, OperationalError) as e:
            # Database errors - never expose to users!
            handle_database_exception(e, "user login")
        except Exception as e:
            # Catch-all for unexpected errors
            handle_database_exception(e, "user login")
        finally:
            db.close()


@strawberry.type
class AuthQuery:
    """
    GraphQL queries for authentication.
    """

    @strawberry.field
    def me(self, info: Info) -> Optional[UserType]:
        """
        Get current authenticated user.
        
        Args:
            info: GraphQL info object
            
        Returns:
            Current user or None (no exceptions, just returns None on any error)
        """
        try:
            # Get token from context
            request = info.context.get("request")
            if not request:
                return None
            
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.replace("Bearer ", "")
            payload = decode_access_token(token)
            
            if not payload:
                return None
            
            public_id = payload.get("sub")
            if not public_id:
                return None
            
            db: Session = next(get_db())
            try:
                # Find user by public_id (UUID) for security
                user = UserService.get_user_by_public_id(db, public_id)
                if not user:
                    return None
                
                return UserType(
                    id=str(user.public_id),  # Use UUID for public API
                    email=user.email,
                    username=user.username,
                    is_active=user.is_active,
                    is_superuser=user.is_superuser
                )
            finally:
                db.close()
        except Exception as e:
            # Log error but return None (don't expose errors in queries)
            logger.error(f"Error in me query: {type(e).__name__}: {str(e)}")
            return None

    @strawberry.field
    def search_users(self, query: str, info: Info, limit: Optional[int] = 10) -> List[UserType]:
        """
        Search users by email or username.
        Requires authentication.
        
        Args:
            query: Search query string
            info: GraphQL info object
            limit: Maximum number of results (default 10)
            
        Returns:
            List of matching users
            
        Raises:
            UnauthorizedError: If user is not authenticated
        """
        try:
            # Check if user is authenticated
            request = info.context.get("request")
            if not request:
                raise UnauthorizedError("Authentication required to search users")
            
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise UnauthorizedError("Authentication required to search users")
            
            token = auth_header.replace("Bearer ", "")
            payload = decode_access_token(token)
            
            if not payload:
                raise UnauthorizedError("Invalid authentication token")
            
            db: Session = next(get_db())
            try:
                users = UserService.search_users(db, query, limit or 10)
                return [
                    UserType(
                        id=str(user.public_id),
                        email=user.email,
                        username=user.username,
                        is_active=user.is_active,
                        is_superuser=user.is_superuser
                    )
                    for user in users
                ]
            finally:
                db.close()
        except UnauthorizedError:
            raise
        except Exception as e:
            logger.error(f"Error in search_users query: {type(e).__name__}: {str(e)}")
            return []

