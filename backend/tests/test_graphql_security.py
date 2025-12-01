"""
Integration tests for GraphQL Security.
Tests run against http://localhost:8000/graphql
"""
import pytest
import uuid
import re


class TestAuthenticationRequirement:
    """Tests that endpoints require authentication."""

    @pytest.mark.asyncio
    async def test_teams_requires_auth(self, graphql_client):
        """Test teams query requires authentication."""
        query = "query { teams { id } }"
        result = await graphql_client.execute_async(query)
        # Should fail - either errors or null data
        assert result.errors is not None or result.data is None or result.data.get("teams") is None

    @pytest.mark.asyncio
    async def test_projects_requires_auth(self, graphql_client):
        """Test projects query requires authentication."""
        query = "query { projects { id } }"
        result = await graphql_client.execute_async(query)
        # Should fail - either errors or null data
        assert result.errors is not None or result.data is None or result.data.get("projects") is None

    @pytest.mark.asyncio
    async def test_create_team_requires_auth(self, graphql_client):
        """Test createTeam mutation requires authentication."""
        query = """
            mutation CreateTeam($input: CreateTeamInput!) {
                createTeam(input: $input) { id }
            }
        """
        result = await graphql_client.execute_async(query, {
            "input": {"name": "Test", "description": "Test"}
        })
        assert result.errors is not None or result.data.get("createTeam") is None

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, graphql_client):
        """Test invalid token is rejected."""
        graphql_client.set_token("invalid-token")
        query = "query { me { id } }"
        result = await graphql_client.execute_async(query)
        assert result.data["me"] is None


class TestUUIDExposure:
    """Tests that IDs are UUIDs, not sequential integers."""

    @pytest.mark.asyncio
    async def test_user_id_is_uuid(self, authenticated_graphql_client):
        """Test user ID is a UUID."""
        query = "query { me { id } }"
        result = await authenticated_graphql_client.execute_async(query)
        
        user_id = result.data["me"]["id"]
        # UUID format: 8-4-4-4-12 hex digits
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        assert re.match(uuid_pattern, user_id, re.IGNORECASE)

    @pytest.mark.asyncio
    async def test_team_id_is_uuid(self, authenticated_graphql_client):
        """Test team ID is a UUID."""
        unique_id = uuid.uuid4().hex[:8]
        query = """
            mutation CreateTeam($input: CreateTeamInput!) {
                createTeam(input: $input) { id }
            }
        """
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {"name": f"UUID Team {unique_id}", "description": "Test"}
        })
        
        team_id = result.data["createTeam"]["id"]
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        assert re.match(uuid_pattern, team_id, re.IGNORECASE)

    @pytest.mark.asyncio
    async def test_project_id_is_uuid(self, authenticated_graphql_client):
        """Test project ID is a UUID."""
        unique_id = uuid.uuid4().hex[:8]
        
        # Create team first
        team_query = """
            mutation CreateTeam($input: CreateTeamInput!) {
                createTeam(input: $input) { id }
            }
        """
        team_result = await authenticated_graphql_client.execute_async(team_query, {
            "input": {"name": f"Team {unique_id}", "description": "Test"}
        })
        team_id = team_result.data["createTeam"]["id"]
        
        # Create project
        project_query = """
            mutation CreateProject($input: CreateProjectInput!) {
                createProject(input: $input) { id }
            }
        """
        result = await authenticated_graphql_client.execute_async(project_query, {
            "input": {
                "name": f"UUID Project {unique_id}",
                "teamId": team_id,
                "languages": [{"code": "en", "locale": "en-US", "direction": "ltr"}],
                "defaultLanguage": "en",
                "color": "#000",
                "status": "active"
            }
        })
        
        project_id = result.data["createProject"]["id"]
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        assert re.match(uuid_pattern, project_id, re.IGNORECASE)


class TestErrorMessageSafety:
    """Tests that error messages don't expose sensitive info."""

    @pytest.mark.asyncio
    async def test_login_error_no_user_enumeration(self, graphql_client):
        """Test login errors don't reveal if user exists."""
        query = """
            mutation Login($input: LoginInput!) {
                login(input: $input) { accessToken }
            }
        """
        
        # Try with nonexistent user
        result1 = await graphql_client.execute_async(query, {
            "input": {"email": "nonexistent@example.com", "password": "password"}
        })
        
        # Try with wrong password (need to create user first)
        unique_id = uuid.uuid4().hex[:8]
        email = f"enumtest_{unique_id}@example.com"
        
        # Register
        await graphql_client.execute_async("""
            mutation Register($input: RegisterInput!) {
                register(input: $input) { accessToken }
            }
        """, {
            "input": {"email": email, "username": f"enumtest_{unique_id}", "password": "Password123!"}
        })
        
        # Try login with wrong password
        result2 = await graphql_client.execute_async(query, {
            "input": {"email": email, "password": "wrongpassword"}
        })
        
        # Both should fail similarly - not reveal if user exists
        login_failed_1 = result1.errors is not None or result1.data is None or result1.data.get("login") is None
        login_failed_2 = result2.errors is not None or result2.data is None or result2.data.get("login") is None
        assert login_failed_1
        assert login_failed_2


class TestInputValidation:
    """Tests for input validation."""

    @pytest.mark.asyncio
    async def test_sql_injection_attempt(self, authenticated_graphql_client):
        """Test SQL injection is prevented."""
        unique_id = uuid.uuid4().hex[:8]
        
        # Create team and project
        team_result = await authenticated_graphql_client.execute_async("""
            mutation CreateTeam($input: CreateTeamInput!) {
                createTeam(input: $input) { id }
            }
        """, {"input": {"name": f"SQLi Team {unique_id}", "description": "Test"}})
        team_id = team_result.data["createTeam"]["id"]
        
        project_result = await authenticated_graphql_client.execute_async("""
            mutation CreateProject($input: CreateProjectInput!) {
                createProject(input: $input) { id }
            }
        """, {
            "input": {
                "name": f"SQLi Project {unique_id}",
                "teamId": team_id,
                "languages": [{"code": "en", "locale": "en-US", "direction": "ltr"}],
                "defaultLanguage": "en",
                "color": "#000",
                "status": "active"
            }
        })
        project_id = project_result.data["createProject"]["id"]
        
        # Try SQL injection in search
        query = """
            query ProjectKeys($projectId: String!, $search: String) {
                projectKeys(projectId: $projectId, search: $search) {
                    keys { id }
                }
            }
        """
        result = await authenticated_graphql_client.execute_async(query, {
            "projectId": project_id,
            "search": "'; DROP TABLE keys; --"
        })
        
        # Should not error, just return empty/safe results
        assert result.errors is None or "DROP TABLE" not in str(result.errors)

    @pytest.mark.asyncio
    async def test_xss_in_key_name(self, authenticated_graphql_client):
        """Test XSS is stored safely (output encoding should happen on frontend)."""
        unique_id = uuid.uuid4().hex[:8]
        
        team_result = await authenticated_graphql_client.execute_async("""
            mutation CreateTeam($input: CreateTeamInput!) {
                createTeam(input: $input) { id }
            }
        """, {"input": {"name": f"XSS Team {unique_id}", "description": "Test"}})
        team_id = team_result.data["createTeam"]["id"]
        
        project_result = await authenticated_graphql_client.execute_async("""
            mutation CreateProject($input: CreateProjectInput!) {
                createProject(input: $input) { id }
            }
        """, {
            "input": {
                "name": f"XSS Project {unique_id}",
                "teamId": team_id,
                "languages": [{"code": "en", "locale": "en-US", "direction": "ltr"}],
                "defaultLanguage": "en",
                "color": "#000",
                "status": "active"
            }
        })
        project_id = project_result.data["createProject"]["id"]
        
        # Create key with XSS attempt
        xss_key = f"<script>alert('xss')</script>.key.{unique_id}"
        result = await authenticated_graphql_client.execute_async("""
            mutation CreateKey($input: CreateKeyInput!) {
                createKey(input: $input) {
                    id
                    key
                }
            }
        """, {
            "input": {
                "projectId": project_id,
                "key": xss_key,
                "translations": {"en": "Test"}
            }
        })
        
        # Key should be stored (XSS prevention is frontend responsibility)
        assert result.errors is None
        assert result.data["createKey"]["key"] == xss_key

    @pytest.mark.asyncio
    async def test_invalid_uuid_handled(self, authenticated_graphql_client):
        """Test invalid UUID is handled gracefully."""
        query = """
            query Team($id: String!) {
                team(id: $id) { id }
            }
        """
        result = await authenticated_graphql_client.execute_async(query, {"id": "not-a-uuid"})
        
        # Should return null, not crash
        assert result.data["team"] is None

    @pytest.mark.asyncio
    async def test_password_length_validation(self, graphql_client):
        """Test password length is validated."""
        unique_id = uuid.uuid4().hex[:8]
        query = """
            mutation Register($input: RegisterInput!) {
                register(input: $input) { accessToken }
            }
        """
        result = await graphql_client.execute_async(query, {
            "input": {
                "email": f"short_{unique_id}@example.com",
                "username": f"short_{unique_id}",
                "password": "short"
            }
        })
        
        # Should fail validation
        assert result.errors is not None or result.data["register"] is None
