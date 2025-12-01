import strawberry
from typing import Optional
from datetime import timedelta
from strawberry.types import Info
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
import logging

from app.database import get_db
from app.services.user_service import UserService
from app.services.email_service import send_welcome_email_background, send_password_reset_email_background
from app.core.security import create_access_token, decode_access_token
from app.core.exceptions import (
    AuthenticationError,
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
    onboarding_completed: bool


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


@strawberry.input
class RequestPasswordResetInput:
    """
    Input type for requesting password reset.
    """
    email: str


@strawberry.input
class ResetPasswordInput:
    """
    Input type for resetting password with token.
    """
    token: str
    new_password: str


@strawberry.input
class UpdateProfileInput:
    """
    Input type for updating user profile.
    """
    username: Optional[str] = None
    email: Optional[str] = None


@strawberry.input
class ChangePasswordInput:
    """
    Input type for changing password.
    """
    current_password: str
    new_password: str


@strawberry.type
class ProfileUpdateResult:
    """
    Result type for profile update operations.
    """
    success: bool
    message: str
    user: Optional[UserType] = None


@strawberry.type
class PasswordResetResult:
    """
    Result type for password reset operations.
    """
    success: bool
    message: str


@strawberry.type
class AuthMutation:
    """
    GraphQL mutations for authentication.
    """

    @strawberry.mutation
    def register(self, input: RegisterInput, info: Info) -> AuthPayload:
        """
        Register a new user.
        
        If user has pending team invitations, onboarding is skipped.
        
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
        from app.services.team_service import TeamService
        from app.models.team_invitation import TeamInvitation, InvitationStatus
        
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
            
            # Check if there are pending invitations for this email
            pending_invites = TeamService.get_pending_invitations_for_email(db, input.email)
            has_pending_invites = len(pending_invites) > 0
            
            # Create user - skip onboarding if user has pending invites
            user = UserService.create_user(
                db=db,
                email=input.email,
                username=input.username,
                password=input.password
            )
            
            # If user has pending invites, mark onboarding as completed
            # (they will accept invites instead of creating a new team)
            if has_pending_invites:
                user.onboarding_completed = True
                # Link pending invitations to this user
                for invite in pending_invites:
                    invite.invited_user_id = user.id
                db.commit()
                db.refresh(user)
                logger.info(f"User {user.email} registered with {len(pending_invites)} pending invitations, onboarding skipped")
            
            # Create access token using public_id (UUID) for security
            access_token = create_access_token(data={"sub": str(user.public_id)})
            
            # Send welcome email in background thread (fire and forget)
            # Email failure should not affect registration success
            try:
                send_welcome_email_background(user.email, user.username)
            except Exception as e:
                # Log but don't fail registration if email scheduling fails
                logger.warning(f"Failed to schedule welcome email for {user.email}: {type(e).__name__}")
            
            return AuthPayload(
                access_token=access_token,
                token_type="bearer",
                user=UserType(
                    id=str(user.public_id),  # Use UUID for public API
                    email=user.email,
                    username=user.username,
                    is_active=user.is_active,
                    is_superuser=user.is_superuser,
                    onboarding_completed=user.onboarding_completed
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
                    is_superuser=user.is_superuser,
                    onboarding_completed=user.onboarding_completed
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

    @strawberry.mutation
    def request_password_reset(self, input: RequestPasswordResetInput, info: Info) -> PasswordResetResult:
        """
        Request a password reset email.
        
        Always returns success to prevent email enumeration attacks.
        If email doesn't exist, we just don't send the email but return success anyway.
        
        Args:
            input: Email address for password reset
            info: GraphQL info object
            
        Returns:
            PasswordResetResult with success status and message
        """
        db: Session = next(get_db())
        
        try:
            # Find user by email
            user = UserService.get_user_by_email(db, input.email)
            
            if user and user.is_active:
                # Create reset token
                reset_token = UserService.create_password_reset_token(db, user)
                
                # Send email in background
                try:
                    send_password_reset_email_background(
                        email=user.email,
                        username=user.username,
                        reset_token=reset_token.token
                    )
                except Exception as e:
                    # Log but don't fail the request
                    logger.warning(f"Failed to schedule password reset email for {user.email}: {type(e).__name__}")
            else:
                # User doesn't exist or is inactive - log but don't reveal
                logger.info(f"Password reset requested for non-existent or inactive email: {input.email}")
            
            # Always return success to prevent email enumeration
            return PasswordResetResult(
                success=True,
                message="If an account with this email exists, a password reset link has been sent."
            )
        except (IntegrityError, OperationalError) as e:
            # Database errors - never expose to users!
            logger.error(f"Database error in password reset request: {type(e).__name__}")
            return PasswordResetResult(
                success=True,
                message="If an account with this email exists, a password reset link has been sent."
            )
        except Exception as e:
            # Catch-all - still return success to prevent enumeration
            logger.error(f"Error in password reset request: {type(e).__name__}")
            return PasswordResetResult(
                success=True,
                message="If an account with this email exists, a password reset link has been sent."
            )
        finally:
            db.close()

    @strawberry.mutation
    def reset_password(self, input: ResetPasswordInput, info: Info) -> PasswordResetResult:
        """
        Reset password using a valid token.
        
        Args:
            input: Token and new password
            info: GraphQL info object
            
        Returns:
            PasswordResetResult with success status and message
        """
        db: Session = next(get_db())
        
        try:
            # Validate password
            if len(input.new_password) < 8:
                return PasswordResetResult(
                    success=False,
                    message="Password must be at least 8 characters long."
                )
            if len(input.new_password) > 72:
                return PasswordResetResult(
                    success=False,
                    message="Password must be no more than 72 characters long."
                )
            
            # Attempt to reset password
            success = UserService.reset_password(db, input.token, input.new_password)
            
            if success:
                return PasswordResetResult(
                    success=True,
                    message="Your password has been reset successfully. You can now sign in with your new password."
                )
            else:
                return PasswordResetResult(
                    success=False,
                    message="This password reset link is invalid or has expired. Please request a new one."
                )
        except (IntegrityError, OperationalError) as e:
            # Database errors - user-friendly message
            logger.error(f"Database error in password reset: {type(e).__name__}")
            return PasswordResetResult(
                success=False,
                message="Unable to reset password. Please try again."
            )
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Error in password reset: {type(e).__name__}")
            return PasswordResetResult(
                success=False,
                message="Unable to reset password. Please try again."
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
                    is_superuser=user.is_superuser,
                    onboarding_completed=user.onboarding_completed
                )
            finally:
                db.close()
        except Exception as e:
            # Log error but return None (don't expose errors in queries)
            logger.error(f"Error in me query: {type(e).__name__}: {str(e)}")
            return None


@strawberry.type
class ProfileMutation:
    """
    GraphQL mutations for profile management.
    """

    @strawberry.mutation
    def update_profile(self, input: UpdateProfileInput, info: Info) -> ProfileUpdateResult:
        """
        Update user profile (username and/or email).
        
        Args:
            input: Profile update data
            info: GraphQL info object
            
        Returns:
            ProfileUpdateResult with success status and updated user
            
        Raises:
            AuthenticationError: If user is not authenticated
        """
        try:
            # Get token from context
            request = info.context.get("request")
            if not request:
                raise AuthenticationError()
            
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise AuthenticationError()
            
            token = auth_header.replace("Bearer ", "")
            payload = decode_access_token(token)
            
            if not payload:
                raise AuthenticationError()
            
            public_id = payload.get("sub")
            if not public_id:
                raise AuthenticationError()
            
            db: Session = next(get_db())
            try:
                # Find user by public_id (UUID)
                user = UserService.get_user_by_public_id(db, public_id)
                if not user:
                    raise AuthenticationError()
                
                # Check if new email is already taken
                if input.email and input.email != user.email:
                    existing = UserService.get_user_by_email(db, input.email)
                    if existing:
                        return ProfileUpdateResult(
                            success=False,
                            message="This email is already in use.",
                            user=None
                        )
                
                # Check if new username is already taken
                if input.username and input.username != user.username:
                    existing = UserService.get_user_by_username(db, input.username)
                    if existing:
                        return ProfileUpdateResult(
                            success=False,
                            message="This username is already taken.",
                            user=None
                        )
                
                # Update profile
                updated_user = UserService.update_profile(
                    db=db,
                    user=user,
                    username=input.username,
                    email=input.email
                )
                
                return ProfileUpdateResult(
                    success=True,
                    message="Profile updated successfully.",
                    user=UserType(
                        id=str(updated_user.public_id),
                        email=updated_user.email,
                        username=updated_user.username,
                        is_active=updated_user.is_active,
                        is_superuser=updated_user.is_superuser,
                        onboarding_completed=updated_user.onboarding_completed
                    )
                )
            finally:
                db.close()
        except AuthenticationError:
            raise
        except (IntegrityError, OperationalError) as e:
            logger.error(f"Database error in profile update: {type(e).__name__}")
            return ProfileUpdateResult(
                success=False,
                message="Unable to update profile. Please try again.",
                user=None
            )
        except Exception as e:
            logger.error(f"Error in profile update: {type(e).__name__}")
            return ProfileUpdateResult(
                success=False,
                message="Unable to update profile. Please try again.",
                user=None
            )

    @strawberry.mutation
    def change_password(self, input: ChangePasswordInput, info: Info) -> ProfileUpdateResult:
        """
        Change user password.
        
        Args:
            input: Current and new password
            info: GraphQL info object
            
        Returns:
            ProfileUpdateResult with success status
            
        Raises:
            AuthenticationError: If user is not authenticated
        """
        try:
            # Get token from context
            request = info.context.get("request")
            if not request:
                raise AuthenticationError()
            
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise AuthenticationError()
            
            token = auth_header.replace("Bearer ", "")
            payload = decode_access_token(token)
            
            if not payload:
                raise AuthenticationError()
            
            public_id = payload.get("sub")
            if not public_id:
                raise AuthenticationError()
            
            # Validate new password
            if len(input.new_password) < 8:
                return ProfileUpdateResult(
                    success=False,
                    message="Password must be at least 8 characters long.",
                    user=None
                )
            if len(input.new_password) > 72:
                return ProfileUpdateResult(
                    success=False,
                    message="Password must be no more than 72 characters long.",
                    user=None
                )
            
            db: Session = next(get_db())
            try:
                # Find user by public_id (UUID)
                user = UserService.get_user_by_public_id(db, public_id)
                if not user:
                    raise AuthenticationError()
                
                # Change password
                success = UserService.change_password(
                    db=db,
                    user=user,
                    current_password=input.current_password,
                    new_password=input.new_password
                )
                
                if success:
                    return ProfileUpdateResult(
                        success=True,
                        message="Password changed successfully.",
                        user=UserType(
                            id=str(user.public_id),
                            email=user.email,
                            username=user.username,
                            is_active=user.is_active,
                            is_superuser=user.is_superuser,
                            onboarding_completed=user.onboarding_completed
                        )
                    )
                else:
                    return ProfileUpdateResult(
                        success=False,
                        message="Current password is incorrect.",
                        user=None
                    )
            finally:
                db.close()
        except AuthenticationError:
            raise
        except (IntegrityError, OperationalError) as e:
            logger.error(f"Database error in password change: {type(e).__name__}")
            return ProfileUpdateResult(
                success=False,
                message="Unable to change password. Please try again.",
                user=None
            )
        except Exception as e:
            logger.error(f"Error in password change: {type(e).__name__}")
            return ProfileUpdateResult(
                success=False,
                message="Unable to change password. Please try again.",
                user=None
            )


@strawberry.type
class OnboardingMutation:
    """
    GraphQL mutations for onboarding management.
    """

    @strawberry.mutation
    def complete_onboarding(self, info: Info) -> UserType:
        """
        Mark user's onboarding as completed.
        
        Args:
            info: GraphQL info object with authenticated user
            
        Returns:
            Updated user with onboarding_completed = True
            
        Raises:
            AuthenticationError: If user is not authenticated
            DatabaseError: If database operation fails
        """
        try:
            # Get token from context
            request = info.context.get("request")
            if not request:
                raise AuthenticationError()
            
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise AuthenticationError()
            
            token = auth_header.replace("Bearer ", "")
            payload = decode_access_token(token)
            
            if not payload:
                raise AuthenticationError()
            
            public_id = payload.get("sub")
            if not public_id:
                raise AuthenticationError()
            
            db: Session = next(get_db())
            try:
                # Find user by public_id (UUID)
                user = UserService.get_user_by_public_id(db, public_id)
                if not user:
                    raise AuthenticationError()
                
                # Update onboarding status
                user.onboarding_completed = True
                db.commit()
                db.refresh(user)
                
                logger.info(f"User {user.email} completed onboarding")
                
                return UserType(
                    id=str(user.public_id),
                    email=user.email,
                    username=user.username,
                    is_active=user.is_active,
                    is_superuser=user.is_superuser,
                    onboarding_completed=user.onboarding_completed
                )
            finally:
                db.close()
        except AuthenticationError:
            raise
        except (IntegrityError, OperationalError) as e:
            handle_database_exception(e, "complete onboarding")
        except Exception as e:
            handle_database_exception(e, "complete onboarding")


