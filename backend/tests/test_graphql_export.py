"""
Integration tests for Project Export API.
Tests run against http://localhost:8000
"""
import pytest
import uuid


# ============================================================================
# Helper functions
# ============================================================================

async def create_team(client) -> str:
    """Helper to create a team."""
    unique_id = uuid.uuid4().hex[:8]
    query = """
        mutation CreateTeam($input: CreateTeamInput!) {
            createTeam(input: $input) { id }
        }
    """
    result = await client.execute_async(query, {
        "input": {"name": f"Team {unique_id}", "description": "Test team for export"}
    })
    return result.data["createTeam"]["id"]


async def create_project_with_keys(client, team_id: str) -> str:
    """Helper to create a project with keys and translations."""
    unique_id = uuid.uuid4().hex[:8]
    
    # Create project
    query = """
        mutation CreateProject($input: CreateProjectInput!) {
            createProject(input: $input) { id }
        }
    """
    result = await client.execute_async(query, {
        "input": {
            "name": f"ExportTest {unique_id}",
            "description": "Project for export testing",
            "teamId": team_id,
            "languages": [
                {"code": "en", "locale": "en-US", "direction": "ltr"},
                {"code": "ru", "locale": "ru-RU", "direction": "ltr"}
            ],
            "defaultLanguage": "en",
            "color": "#6366f1",
            "status": "active"
        }
    })
    project_id = result.data["createProject"]["id"]
    
    # Create some keys
    for i in range(3):
        await client.execute_async("""
            mutation CreateKey($input: CreateKeyInput!) {
                createKey(input: $input) { id }
            }
        """, {
            "input": {
                "projectId": project_id,
                "key": f"test.key.{i}",
                "description": f"Test key {i}",
                "translations": {"en": f"English {i}", "ru": f"Russian {i}"}
            }
        })
    
    return project_id


# ============================================================================
# Export Tests
# ============================================================================

class TestProjectExport:
    """Tests for project export REST API."""

    @pytest.mark.asyncio
    async def test_export_project_returns_json(self, authenticated_graphql_client):
        """Test that export returns valid JSON with project data."""
        import httpx
        
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project_with_keys(authenticated_graphql_client, team_id)
        
        # Export via REST API
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"http://localhost:8000/api/projects/{project_id}/export",
                headers={"Authorization": f"Bearer {authenticated_graphql_client._token}"},
                timeout=30.0
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "name" in data
        assert "config" in data
        assert "keys" in data
        assert "locales" in data
        
        # Verify keys
        assert len(data["keys"]) == 3
        
        # Verify locales
        assert len(data["locales"]) == 2

    @pytest.mark.asyncio
    async def test_export_creates_activity_log(self, authenticated_graphql_client):
        """Test that export creates PROJECT_EXPORT activity log."""
        import httpx
        
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project_with_keys(authenticated_graphql_client, team_id)
        
        # Export via REST API
        async with httpx.AsyncClient() as http_client:
            await http_client.get(
                f"http://localhost:8000/api/projects/{project_id}/export",
                headers={"Authorization": f"Bearer {authenticated_graphql_client._token}"},
                timeout=30.0
            )
        
        # Check activity log
        query = """
            query ProjectActivity($projectId: String!) {
                projectActivity(projectId: $projectId) {
                    id
                    action
                }
            }
        """
        result = await authenticated_graphql_client.execute_async(query, {
            "projectId": project_id
        })
        
        assert result.errors is None
        actions = [log["action"] for log in result.data["projectActivity"]]
        assert "PROJECT_EXPORT" in actions

    @pytest.mark.asyncio
    async def test_export_unauthenticated_fails(self):
        """Test that export fails without authentication."""
        import httpx
        
        fake_project_id = str(uuid.uuid4())
        
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"http://localhost:8000/api/projects/{fake_project_id}/export",
                timeout=30.0
            )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_export_nonexistent_project_fails(self, authenticated_graphql_client):
        """Test that export fails for non-existent project."""
        import httpx
        
        fake_project_id = str(uuid.uuid4())
        
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"http://localhost:8000/api/projects/{fake_project_id}/export",
                headers={"Authorization": f"Bearer {authenticated_graphql_client._token}"},
                timeout=30.0
            )
        
        assert response.status_code == 404

