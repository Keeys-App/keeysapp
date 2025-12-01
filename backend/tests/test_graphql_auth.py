"""
Integration tests for GraphQL Auth API.
Tests run against http://localhost:8000/graphql
"""
import pytest
import uuid


class TestRegisterMutation:
    """Tests for register mutation."""

    @pytest.mark.asyncio
    async def test_register_success(self, graphql_client):
        """Test successful user registration."""
        unique_id = uuid.uuid4().hex[:8]
        
        query = """
            mutation Register($input: RegisterInput!) {
                register(input: $input) {
                    accessToken
                    user {
                        id
                        email
                        username
                    }
                }
            }
        """
        variables = {
            "input": {
                "email": f"newuser_{unique_id}@example.com",
                "username": f"newuser_{unique_id}",
                "password": "SecurePassword123!"
            }
        }
        
        result = await graphql_client.execute_async(query, variables)
        
        assert result.errors is None
        assert result.data["register"]["accessToken"] is not None
        assert result.data["register"]["user"]["email"] == variables["input"]["email"]
        assert result.data["register"]["user"]["username"] == variables["input"]["username"]

    @pytest.mark.asyncio
    async def test_register_short_password(self, graphql_client):
        """Test registration fails with short password."""
        unique_id = uuid.uuid4().hex[:8]
        
        query = """
            mutation Register($input: RegisterInput!) {
                register(input: $input) {
                    accessToken
                    user { id }
                }
            }
        """
        variables = {
            "input": {
                "email": f"user_{unique_id}@example.com",
                "username": f"user_{unique_id}",
                "password": "short"
            }
        }
        
        result = await graphql_client.execute_async(query, variables)
        
        # Should have an error about password length
        assert result.errors is not None or result.data["register"] is None


class TestLoginMutation:
    """Tests for login mutation."""

    @pytest.mark.asyncio
    async def test_login_success(self, graphql_client):
        """Test successful login."""
        unique_id = uuid.uuid4().hex[:8]
        email = f"login_test_{unique_id}@example.com"
        password = "TestPassword123!"
        
        # First register
        register_query = """
            mutation Register($input: RegisterInput!) {
                register(input: $input) {
                    accessToken
                }
            }
        """
        await graphql_client.execute_async(register_query, {
            "input": {
                "email": email,
                "username": f"logintest_{unique_id}",
                "password": password
            }
        })
        
        # Then login
        login_query = """
            mutation Login($input: LoginInput!) {
                login(input: $input) {
                    accessToken
                    user {
                        email
                    }
                }
            }
        """
        result = await graphql_client.execute_async(login_query, {
            "input": {
                "email": email,
                "password": password
            }
        })
        
        assert result.errors is None
        assert result.data["login"]["accessToken"] is not None
        assert result.data["login"]["user"]["email"] == email

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, graphql_client):
        """Test login fails with wrong password."""
        unique_id = uuid.uuid4().hex[:8]
        email = f"wrongpw_{unique_id}@example.com"
        
        # Register
        register_query = """
            mutation Register($input: RegisterInput!) {
                register(input: $input) { accessToken }
            }
        """
        await graphql_client.execute_async(register_query, {
            "input": {
                "email": email,
                "username": f"wrongpw_{unique_id}",
                "password": "CorrectPassword123!"
            }
        })
        
        # Login with wrong password
        login_query = """
            mutation Login($input: LoginInput!) {
                login(input: $input) {
                    accessToken
                }
            }
        """
        result = await graphql_client.execute_async(login_query, {
            "input": {
                "email": email,
                "password": "WrongPassword123!"
            }
        })
        
        # Should fail - either errors or null data
        assert result.errors is not None or result.data is None or result.data.get("login") is None

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, graphql_client):
        """Test login fails for nonexistent user."""
        query = """
            mutation Login($input: LoginInput!) {
                login(input: $input) {
                    accessToken
                }
            }
        """
        result = await graphql_client.execute_async(query, {
            "input": {
                "email": "nonexistent@example.com",
                "password": "SomePassword123!"
            }
        })
        
        # Should fail - either errors or null data
        assert result.errors is not None or result.data is None or result.data.get("login") is None


class TestMeQuery:
    """Tests for me query."""

    @pytest.mark.asyncio
    async def test_me_authenticated(self, authenticated_graphql_client):
        """Test me query returns current user."""
        query = """
            query Me {
                me {
                    id
                    email
                    username
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query)
        
        assert result.errors is None
        assert result.data["me"]["email"] == authenticated_graphql_client.test_user["email"]

    @pytest.mark.asyncio
    async def test_me_unauthenticated(self, graphql_client):
        """Test me query fails when not authenticated."""
        query = """
            query Me {
                me {
                    id
                    email
                }
            }
        """
        
        result = await graphql_client.execute_async(query)
        
        assert result.data["me"] is None


class TestProfileMutation:
    """Tests for profile update mutations."""

    @pytest.mark.asyncio
    async def test_update_profile_username(self, authenticated_graphql_client):
        """Test updating username."""
        new_username = f"updated_{uuid.uuid4().hex[:8]}"
        
        query = """
            mutation UpdateProfile($input: UpdateProfileInput!) {
                updateProfile(input: $input) {
                    success
                    user {
                        username
                    }
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {"username": new_username}
        })
        
        assert result.errors is None
        assert result.data["updateProfile"]["success"] is True
        assert result.data["updateProfile"]["user"]["username"] == new_username

    @pytest.mark.asyncio
    async def test_update_profile_unauthenticated(self, graphql_client):
        """Test profile update fails when not authenticated."""
        query = """
            mutation UpdateProfile($input: UpdateProfileInput!) {
                updateProfile(input: $input) {
                    id
                }
            }
        """
        
        result = await graphql_client.execute_async(query, {
            "input": {"username": "newname"}
        })
        
        # Should fail - either errors or null data
        assert result.errors is not None or result.data is None or result.data.get("updateProfile") is None


class TestChangePasswordMutation:
    """Tests for password change mutation."""

    @pytest.mark.asyncio
    async def test_change_password_success(self, graphql_client):
        """Test successful password change."""
        unique_id = uuid.uuid4().hex[:8]
        email = f"changepw_{unique_id}@example.com"
        old_password = "OldPassword123!"
        new_password = "NewPassword456!"
        
        # Register
        register_query = """
            mutation Register($input: RegisterInput!) {
                register(input: $input) {
                    accessToken
                }
            }
        """
        reg_result = await graphql_client.execute_async(register_query, {
            "input": {
                "email": email,
                "username": f"changepw_{unique_id}",
                "password": old_password
            }
        })
        
        token = reg_result.data["register"]["accessToken"]
        graphql_client.set_token(token)
        
        # Change password (returns ProfileUpdateResult with success, message, user)
        change_query = """
            mutation ChangePassword($input: ChangePasswordInput!) {
                changePassword(input: $input) {
                    success
                    message
                }
            }
        """
        result = await graphql_client.execute_async(change_query, {
            "input": {
                "currentPassword": old_password,
                "newPassword": new_password
            }
        })
        
        assert result.errors is None
        assert result.data["changePassword"]["success"] is True
        
        # Verify can login with new password
        graphql_client.clear_token()
        login_query = """
            mutation Login($input: LoginInput!) {
                login(input: $input) {
                    accessToken
                }
            }
        """
        login_result = await graphql_client.execute_async(login_query, {
            "input": {
                "email": email,
                "password": new_password
            }
        })
        
        assert login_result.data["login"]["accessToken"] is not None


class TestOnboardingMutation:
    """Tests for onboarding mutation."""

    @pytest.mark.asyncio
    async def test_complete_onboarding(self, authenticated_graphql_client):
        """Test completing onboarding."""
        query = """
            mutation CompleteOnboarding {
                completeOnboarding {
                    id
                    onboardingCompleted
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query)
        
        assert result.errors is None
        assert result.data["completeOnboarding"]["onboardingCompleted"] is True
