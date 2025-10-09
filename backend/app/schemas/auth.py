import strawberry
from typing import Optional
from datetime import timedelta
from strawberry.types import Info
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.user_service import UserService
from app.core.security import create_access_token, decode_access_token


@strawberry.type
class UserType:
    """
    GraphQL type for User.
    """
    id: int
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
            Exception: If email or username already exists
        """
        db: Session = next(get_db())
        
        try:
            # Check if email already exists
            existing_user = UserService.get_user_by_email(db, input.email)
            if existing_user:
                raise Exception("Email already registered")
            
            # Check if username already exists
            existing_username = UserService.get_user_by_username(db, input.username)
            if existing_username:
                raise Exception("Username already taken")
            
            # Create user
            user = UserService.create_user(
                db=db,
                email=input.email,
                username=input.username,
                password=input.password
            )
            
            # Create access token
            access_token = create_access_token(data={"sub": str(user.id)})
            
            return AuthPayload(
                access_token=access_token,
                token_type="bearer",
                user=UserType(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    is_active=user.is_active,
                    is_superuser=user.is_superuser
                )
            )
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
            Exception: If authentication fails
        """
        db: Session = next(get_db())
        
        try:
            # Authenticate user
            user = UserService.authenticate_user(db, input.email, input.password)
            if not user:
                raise Exception("Invalid credentials")
            
            # Create access token
            access_token = create_access_token(data={"sub": str(user.id)})
            
            return AuthPayload(
                access_token=access_token,
                token_type="bearer",
                user=UserType(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    is_active=user.is_active,
                    is_superuser=user.is_superuser
                )
            )
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
            Current user or None
        """
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
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        db: Session = next(get_db())
        try:
            user = UserService.get_user_by_id(db, int(user_id))
            if not user:
                return None
            
            return UserType(
                id=user.id,
                email=user.email,
                username=user.username,
                is_active=user.is_active,
                is_superuser=user.is_superuser
            )
        finally:
            db.close()

