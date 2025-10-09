"""
Tests for UUID-based user lookups.
"""
import pytest
from app.services.user_service import UserService


class TestUserServiceUUID:
    """
    Test cases for UUID-based user operations.
    """

    def test_get_user_by_public_id(self, db_session, created_user):
        """
        Test retrieving user by public UUID.
        """
        public_id = str(created_user.public_id)
        user = UserService.get_user_by_public_id(db_session, public_id)

        assert user is not None
        assert user.id == created_user.id
        assert str(user.public_id) == public_id

    def test_get_user_by_public_id_not_found(self, db_session):
        """
        Test retrieving non-existent user by public UUID.
        """
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        user = UserService.get_user_by_public_id(db_session, fake_uuid)
        assert user is None

    def test_get_user_by_invalid_uuid(self, db_session):
        """
        Test retrieving user with invalid UUID string.
        """
        invalid_uuid = "not-a-uuid"
        user = UserService.get_user_by_public_id(db_session, invalid_uuid)
        assert user is None

    def test_public_id_is_unique(self, db_session, sample_user_data):
        """
        Test that each user gets a unique public_id.
        """
        user1 = UserService.create_user(
            db=db_session,
            email="user1@example.com",
            username="user1",
            password="password123"
        )
        
        user2 = UserService.create_user(
            db=db_session,
            email="user2@example.com",
            username="user2",
            password="password123"
        )

        assert user1.public_id != user2.public_id
        assert str(user1.public_id) != str(user2.public_id)

    def test_public_id_is_uuid4(self, created_user):
        """
        Test that public_id is a valid UUID4.
        """
        public_id = created_user.public_id
        
        # Should be UUID object
        assert public_id is not None
        
        # Should have version 4
        assert public_id.version == 4

