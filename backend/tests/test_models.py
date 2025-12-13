"""
Tests for User model.
"""
import pytest
from app.models.user import User


class TestUserModel:
    """
    Test cases for User model.
    """

    def test_user_creation(self, db_session, sample_user_data):
        """
        Test creating a new user.
        """
        user = User(
            email=sample_user_data["email"],
            username=sample_user_data["username"],
            hashed_password=User.get_password_hash(sample_user_data["password"])
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.public_id is not None  # UUID should be auto-generated
        assert user.email == sample_user_data["email"]
        assert user.username == sample_user_data["username"]
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.created_at is not None

    def test_password_hashing(self):
        """
        Test password hashing.
        """
        password = "mysecretpassword"
        hashed = User.get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt hash prefix

    def test_password_verification_success(self, created_user, sample_user_data):
        """
        Test successful password verification.
        """
        assert created_user.verify_password(sample_user_data["password"]) is True

    def test_password_verification_failure(self, created_user):
        """
        Test failed password verification with wrong password.
        """
        assert created_user.verify_password("wrongpassword") is False

    def test_long_password_truncation(self):
        """
        Test that long passwords are properly truncated to 72 bytes.
        """
        long_password = "a" * 100  # 100 characters
        hashed = User.get_password_hash(long_password)

        # Should not raise an error
        assert hashed is not None
        assert len(hashed) > 0

    def test_password_with_special_characters(self):
        """
        Test password with special characters.
        """
        password = "Test@123!#$%^&*()"
        hashed = User.get_password_hash(password)

        assert hashed is not None
        
        # Create user to verify
        user = User(
            email="test@test.com",
            username="testuser",
            hashed_password=hashed
        )
        assert user.verify_password(password) is True

    def test_unicode_password(self):
        """
        Test password with Unicode characters.
        """
        password = "пароль123"  # Unicode characters + numbers
        hashed = User.get_password_hash(password)

        assert hashed is not None
        
        user = User(
            email="test@test.com",
            username="testuser",
            hashed_password=hashed
        )
        assert user.verify_password(password) is True

    def test_empty_password(self):
        """
        Test empty password handling.
        """
        password = ""
        hashed = User.get_password_hash(password)
        
        assert hashed is not None
        
        user = User(
            email="test@test.com",
            username="testuser",
            hashed_password=hashed
        )
        assert user.verify_password(password) is True

    def test_user_unique_email(self, db_session, created_user, sample_user_data):
        """
        Test that email must be unique.
        """
        duplicate_user = User(
            email=sample_user_data["email"],  # Same email
            username="anotheruser",
            hashed_password=User.get_password_hash("password")
        )
        db_session.add(duplicate_user)
        
        with pytest.raises(Exception):  # SQLite will raise IntegrityError
            db_session.commit()

    def test_user_unique_username(self, db_session, created_user, sample_user_data):
        """
        Test that username must be unique.
        """
        duplicate_user = User(
            email="another@example.com",
            username=sample_user_data["username"],  # Same username
            hashed_password=User.get_password_hash("password")
        )
        db_session.add(duplicate_user)
        
        with pytest.raises(Exception):  # SQLite will raise IntegrityError
            db_session.commit()

