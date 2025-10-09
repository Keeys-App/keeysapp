"""
Tests for error handling and security.
Ensures that technical errors are NEVER exposed to users.
"""
import pytest
from sqlalchemy.exc import OperationalError, IntegrityError
from app.core.exceptions import (
    AppException,
    AuthenticationError,
    UserAlreadyExistsError,
    DatabaseError,
    ValidationError,
    handle_database_exception
)


class TestErrorHandling:
    """
    Test cases for proper error handling.
    """

    def test_authentication_error_message_is_safe(self):
        """
        Test that AuthenticationError provides safe message to users.
        """
        error = AuthenticationError(internal_message="User ID 123 not found in database")
        
        # User sees safe message
        assert error.message == "Invalid credentials"
        
        # Technical details only in internal message
        assert "User ID 123" in error.internal_message
        assert "database" in error.internal_message.lower()

    def test_user_already_exists_error_email(self):
        """
        Test UserAlreadyExistsError for email.
        """
        error = UserAlreadyExistsError(
            field="email",
            internal_message="Duplicate key: users.email = 'test@example.com'"
        )
        
        # User sees friendly message
        assert error.message == "Email already registered"
        
        # No SQL details in user message
        assert "Duplicate key" not in error.message
        assert "users.email" not in error.message

    def test_user_already_exists_error_username(self):
        """
        Test UserAlreadyExistsError for username.
        """
        error = UserAlreadyExistsError(field="username")
        
        # User sees friendly message
        assert error.message == "Username already taken"
        
        # No technical details
        assert "duplicate" not in error.message.lower()

    def test_database_error_hides_sql_details(self):
        """
        Test that DatabaseError never exposes SQL or technical details.
        """
        internal_msg = "psycopg.errors.UndefinedColumn: column users.public_id does not exist"
        error = DatabaseError(internal_message=internal_msg)
        
        # User sees generic safe message
        assert error.message == "An error occurred. Please try again later."
        
        # No SQL details in user message
        assert "psycopg" not in error.message
        assert "UndefinedColumn" not in error.message
        assert "public_id" not in error.message
        assert "SQL" not in error.message
        
        # Technical details only in internal message
        assert "psycopg" in error.internal_message
        assert "public_id" in error.internal_message

    def test_validation_error_shows_safe_message(self):
        """
        Test that ValidationError shows safe validation messages.
        """
        error = ValidationError(
            message="Password must be at least 6 characters long",
            internal_message="Password validation failed: length=5"
        )
        
        # User sees helpful validation message
        assert "Password must be at least 6 characters" in error.message
        
        # No code/stack traces
        assert "ValidationError" not in error.message

    def test_handle_database_exception_converts_to_safe_error(self):
        """
        Test that handle_database_exception converts technical errors to safe ones.
        """
        # Simulate database error
        technical_error = OperationalError(
            "SELECT users.id FROM users WHERE users.email = 'test'",
            params={},
            orig=Exception("column users.public_id does not exist")
        )
        
        # Should raise DatabaseError with safe message
        with pytest.raises(DatabaseError) as exc_info:
            handle_database_exception(technical_error, "user lookup")
        
        # User sees generic message
        assert exc_info.value.message == "An error occurred. Please try again later."
        
        # No SQL in user message
        assert "SELECT" not in exc_info.value.message
        assert "users.id" not in exc_info.value.message
        assert "column" not in exc_info.value.message

    def test_integrity_error_handling(self):
        """
        Test that IntegrityError (unique constraint) is properly handled.
        """
        technical_error = IntegrityError(
            "INSERT INTO users (email) VALUES ('test@example.com')",
            params={},
            orig=Exception("duplicate key value violates unique constraint users_email_key")
        )
        
        with pytest.raises(DatabaseError) as exc_info:
            handle_database_exception(technical_error, "user creation")
        
        # User sees generic message
        assert exc_info.value.message == "An error occurred. Please try again later."
        
        # No SQL/constraint details
        assert "INSERT" not in exc_info.value.message
        assert "duplicate key" not in exc_info.value.message
        assert "constraint" not in exc_info.value.message
        assert "users_email_key" not in exc_info.value.message

    def test_app_exception_base_class(self):
        """
        Test that base AppException works correctly.
        """
        safe_msg = "Something went wrong"
        technical_msg = "NullPointerException at line 42 in module.py"
        
        error = AppException(
            message=safe_msg,
            internal_message=technical_msg
        )
        
        # User message is safe
        assert error.message == safe_msg
        assert str(error) == safe_msg
        
        # Technical details in internal message
        assert error.internal_message == technical_msg
        
        # No technical details leak into user message
        assert "NullPointerException" not in error.message
        assert "line 42" not in error.message
        assert "module.py" not in error.message


class TestErrorMessages:
    """
    Test that all error messages are user-friendly and safe.
    """

    def test_no_sql_keywords_in_error_messages(self):
        """
        Test that common SQL keywords never appear in user-facing messages.
        """
        sql_keywords = [
            "SELECT", "INSERT", "UPDATE", "DELETE", "WHERE", "FROM",
            "INNER JOIN", "LEFT JOIN", "GROUP BY", "ORDER BY",
            "psycopg", "SQLAlchemy", "IntegrityError", "OperationalError",
            "column", "table", "constraint", "primary key", "foreign key"
        ]
        
        # Test all custom exceptions
        exceptions = [
            AuthenticationError(),
            UserAlreadyExistsError(field="email"),
            UserAlreadyExistsError(field="username"),
            DatabaseError(),
            ValidationError("Test validation error"),
        ]
        
        for error in exceptions:
            for keyword in sql_keywords:
                assert keyword not in error.message, f"{keyword} found in {type(error).__name__}.message"
                assert keyword.lower() not in error.message.lower(), f"{keyword} found in {type(error).__name__}.message"

    def test_no_file_paths_in_error_messages(self):
        """
        Test that file paths and line numbers never appear in user messages.
        """
        dangerous_patterns = [
            "app/", "backend/", ".py", "line ", "File ", "Traceback",
            "/Users/", "/home/", "C:\\", "venv/", "site-packages/"
        ]
        
        exceptions = [
            AuthenticationError(),
            UserAlreadyExistsError(field="email"),
            DatabaseError(internal_message="/app/models/user.py line 42"),
            ValidationError("Invalid input"),
        ]
        
        for error in exceptions:
            for pattern in dangerous_patterns:
                assert pattern not in error.message, f"{pattern} found in {type(error).__name__}.message"

    def test_no_stack_traces_in_error_messages(self):
        """
        Test that stack traces never appear in user messages.
        """
        stack_keywords = [
            "Traceback", "File", "line", "raise", "except",
            "try:", "finally:", "return", "def ", "class "
        ]
        
        error = DatabaseError(
            internal_message="""
            Traceback (most recent call last):
              File "app/models.py", line 42, in get_user
                return db.query(User).first()
            OperationalError: column does not exist
            """
        )
        
        # Stack trace should NOT be in user message
        for keyword in stack_keywords:
            assert keyword not in error.message

    def test_error_messages_are_helpful(self):
        """
        Test that error messages are helpful to users.
        """
        # Good error messages are:
        # 1. Clear and understandable
        # 2. Actionable (tell user what to do)
        # 3. Professional
        # 4. Not too technical
        
        error = ValidationError("Password must be at least 6 characters long")
        assert len(error.message) > 10  # Not too short
        assert error.message[0].isupper()  # Proper capitalization
        assert isinstance(error.message, str)  # Is a string
        assert len(error.message) < 200  # Not too long

    def test_authentication_error_does_not_reveal_if_user_exists(self):
        """
        Test that authentication errors don't reveal if user exists.
        This prevents user enumeration attacks.
        """
        # Same error for "user not found" and "wrong password"
        error1 = AuthenticationError(internal_message="User not found")
        error2 = AuthenticationError(internal_message="Wrong password")
        
        # Both should have EXACTLY the same user-facing message
        assert error1.message == error2.message
        assert error1.message == "Invalid credentials"


class TestErrorHandlingIntegration:
    """
    Integration tests for error handling in services.
    """

    def test_user_service_get_by_email_handles_db_errors(self, db_session):
        """
        Test that database errors in UserService are handled gracefully.
        """
        from app.services.user_service import UserService
        
        # If database is broken, should not expose SQL errors
        # This test passes if it doesn't crash with SQL error messages
        result = UserService.get_user_by_email(db_session, "test@example.com")
        
        # Result can be None or User, but should not raise SQL exception
        assert result is None or hasattr(result, 'email')

    def test_authentication_service_safe_errors(self, db_session):
        """
        Test that authentication returns safe errors.
        """
        from app.services.user_service import UserService
        
        # Wrong credentials
        result = UserService.authenticate_user(
            db_session,
            "nonexistent@example.com",
            "wrongpassword"
        )
        
        # Should return None, not raise exception with details
        assert result is None


class TestSQLInjectionProtection:
    """
    Test that we're protected against SQL injection.
    """

    def test_email_with_sql_injection_attempt(self, db_session):
        """
        Test that SQL injection in email is handled safely.
        """
        from app.services.user_service import UserService
        
        # Try SQL injection in email
        malicious_email = "admin'--"
        result = UserService.get_user_by_email(db_session, malicious_email)
        
        # Should return None safely, not execute SQL injection
        assert result is None

    def test_username_with_sql_injection_attempt(self, db_session):
        """
        Test that SQL injection in username is handled safely.
        """
        from app.services.user_service import UserService
        
        # Try SQL injection in username
        malicious_username = "admin' OR '1'='1"
        result = UserService.get_user_by_username(db_session, malicious_username)
        
        # Should return None safely
        assert result is None

    def test_password_with_special_sql_characters(self, db_session, sample_user_data):
        """
        Test that passwords with SQL-like characters work correctly.
        """
        from app.services.user_service import UserService
        
        # Password with SQL characters
        sql_password = "'; DROP TABLE users; --"
        
        user = UserService.create_user(
            db=db_session,
            email=sample_user_data["email"],
            username=sample_user_data["username"],
            password=sql_password
        )
        
        # Should create user successfully
        assert user is not None
        
        # Should authenticate with that password
        auth_user = UserService.authenticate_user(
            db_session,
            sample_user_data["email"],
            sql_password
        )
        
        assert auth_user is not None
        assert auth_user.id == user.id

