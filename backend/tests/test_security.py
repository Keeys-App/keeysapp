"""
Tests for JWT security utilities.
"""
import pytest
from datetime import timedelta
from app.core.security import create_access_token, decode_access_token


class TestJWTSecurity:
    """
    Test cases for JWT token creation and verification.
    """

    def test_create_access_token(self):
        """
        Test creating a JWT access token.
        """
        data = {"sub": "123"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiration(self):
        """
        Test creating a token with custom expiration.
        """
        data = {"sub": "123"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta=expires_delta)

        assert token is not None
        assert isinstance(token, str)

    def test_decode_valid_token(self):
        """
        Test decoding a valid token.
        """
        data = {"sub": "123", "username": "testuser"}
        token = create_access_token(data)

        decoded = decode_access_token(token)

        assert decoded is not None
        assert decoded["sub"] == "123"
        assert decoded["username"] == "testuser"
        assert "exp" in decoded  # Expiration should be added

    def test_decode_invalid_token(self):
        """
        Test decoding an invalid token.
        """
        invalid_token = "invalid.token.here"
        decoded = decode_access_token(invalid_token)

        assert decoded is None

    def test_decode_expired_token(self):
        """
        Test decoding an expired token.
        """
        data = {"sub": "123"}
        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        decoded = decode_access_token(token)

        assert decoded is None

    def test_token_contains_expiration(self):
        """
        Test that created token contains expiration claim.
        """
        data = {"sub": "123"}
        token = create_access_token(data)
        decoded = decode_access_token(token)

        assert decoded is not None
        assert "exp" in decoded
        assert isinstance(decoded["exp"], int)

    def test_different_tokens_for_same_data(self):
        """
        Test that different tokens are created for same data (due to expiration).
        """
        import time
        data = {"sub": "123"}
        token1 = create_access_token(data)
        time.sleep(1)  # Wait 1 second to ensure different expiration
        token2 = create_access_token(data)

        # Tokens should be different due to different expiration times
        assert token1 != token2

