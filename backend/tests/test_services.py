"""
Tests for UserService.
"""
import pytest
from app.services.user_service import UserService
from app.models.user import User


class TestUserService:
    """
    Test cases for UserService.
    """

    def test_create_user(self, db_session, sample_user_data):
        """
        Test creating a user through UserService.
        """
        user = UserService.create_user(
            db=db_session,
            email=sample_user_data["email"],
            username=sample_user_data["username"],
            password=sample_user_data["password"]
        )

        assert user.id is not None
        assert user.public_id is not None  # UUID should be auto-generated
        assert user.email == sample_user_data["email"]
        assert user.username == sample_user_data["username"]
        assert user.verify_password(sample_user_data["password"]) is True

    def test_get_user_by_email(self, db_session, created_user, sample_user_data):
        """
        Test retrieving user by email.
        """
        user = UserService.get_user_by_email(db_session, sample_user_data["email"])

        assert user is not None
        assert user.id == created_user.id
        assert user.email == sample_user_data["email"]

    def test_get_user_by_email_not_found(self, db_session):
        """
        Test retrieving non-existent user by email.
        """
        user = UserService.get_user_by_email(db_session, "nonexistent@example.com")
        assert user is None

    def test_get_user_by_username(self, db_session, created_user, sample_user_data):
        """
        Test retrieving user by username.
        """
        user = UserService.get_user_by_username(db_session, sample_user_data["username"])

        assert user is not None
        assert user.id == created_user.id
        assert user.username == sample_user_data["username"]

    def test_get_user_by_username_not_found(self, db_session):
        """
        Test retrieving non-existent user by username.
        """
        user = UserService.get_user_by_username(db_session, "nonexistentuser")
        assert user is None

    def test_get_user_by_id(self, db_session, created_user):
        """
        Test retrieving user by ID.
        """
        user = UserService.get_user_by_id(db_session, created_user.id)

        assert user is not None
        assert user.id == created_user.id

    def test_get_user_by_id_not_found(self, db_session):
        """
        Test retrieving non-existent user by ID.
        """
        user = UserService.get_user_by_id(db_session, 99999)
        assert user is None

    def test_authenticate_user_success(self, db_session, created_user, sample_user_data):
        """
        Test successful user authentication.
        """
        user = UserService.authenticate_user(
            db_session,
            sample_user_data["email"],
            sample_user_data["password"]
        )

        assert user is not None
        assert user.id == created_user.id
        assert user.email == sample_user_data["email"]

    def test_authenticate_user_wrong_password(self, db_session, created_user, sample_user_data):
        """
        Test authentication with wrong password.
        """
        user = UserService.authenticate_user(
            db_session,
            sample_user_data["email"],
            "wrongpassword"
        )

        assert user is None

    def test_authenticate_user_wrong_email(self, db_session, created_user):
        """
        Test authentication with wrong email.
        """
        user = UserService.authenticate_user(
            db_session,
            "wrong@example.com",
            "anypassword"
        )

        assert user is None

    def test_authenticate_inactive_user(self, db_session, created_user, sample_user_data):
        """
        Test authentication of inactive user.
        """
        # Deactivate user
        created_user.is_active = False
        db_session.commit()

        user = UserService.authenticate_user(
            db_session,
            sample_user_data["email"],
            sample_user_data["password"]
        )

        assert user is None

