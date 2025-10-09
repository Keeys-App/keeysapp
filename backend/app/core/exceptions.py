"""
Custom exceptions and error handling.
All exceptions should provide user-friendly messages without exposing internal details.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AppException(Exception):
    """
    Base application exception.
    All custom exceptions should inherit from this.
    """
    def __init__(
        self,
        message: str,
        internal_message: Optional[str] = None,
        log_level: str = "error"
    ):
        """
        Initialize exception.
        
        Args:
            message: User-friendly message (safe to show to users)
            internal_message: Technical details (only for logs)
            log_level: Logging level (error, warning, info)
        """
        super().__init__(message)
        self.message = message
        self.internal_message = internal_message or message
        
        # Log the internal message
        if log_level == "error":
            logger.error(f"AppException: {self.internal_message}")
        elif log_level == "warning":
            logger.warning(f"AppException: {self.internal_message}")
        else:
            logger.info(f"AppException: {self.internal_message}")


class AuthenticationError(AppException):
    """
    Authentication failed.
    """
    def __init__(self, internal_message: Optional[str] = None):
        super().__init__(
            message="Invalid credentials",
            internal_message=internal_message or "Authentication failed",
            log_level="warning"
        )


class UserAlreadyExistsError(AppException):
    """
    User with this email or username already exists.
    """
    def __init__(self, field: str = "email", internal_message: Optional[str] = None):
        if field == "email":
            message = "Email already registered"
        elif field == "username":
            message = "Username already taken"
        else:
            message = "User already exists"
        
        super().__init__(
            message=message,
            internal_message=internal_message or f"User already exists: {field}",
            log_level="info"
        )


class UserNotFoundError(AppException):
    """
    User not found.
    """
    def __init__(self, internal_message: Optional[str] = None):
        super().__init__(
            message="User not found",
            internal_message=internal_message or "User not found",
            log_level="info"
        )


class DatabaseError(AppException):
    """
    Database operation failed.
    Never expose database details to users!
    """
    def __init__(self, internal_message: Optional[str] = None):
        super().__init__(
            message="An error occurred. Please try again later.",
            internal_message=internal_message or "Database error",
            log_level="error"
        )


class ValidationError(AppException):
    """
    Input validation failed.
    """
    def __init__(self, message: str, internal_message: Optional[str] = None):
        super().__init__(
            message=message,
            internal_message=internal_message or f"Validation error: {message}",
            log_level="info"
        )


def handle_database_exception(e: Exception, operation: str = "operation") -> None:
    """
    Handle database exceptions and convert to user-friendly errors.
    
    Args:
        e: Original exception
        operation: Description of operation that failed
        
    Raises:
        DatabaseError: With user-friendly message
    """
    # Log the full technical error
    logger.error(f"Database error during {operation}: {type(e).__name__}: {str(e)}")
    
    # Raise user-friendly error
    raise DatabaseError(f"Database error during {operation}: {type(e).__name__}")

