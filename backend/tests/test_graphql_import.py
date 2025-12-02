"""
Integration tests for Project Import API.
Tests run against http://localhost:8000
"""
import pytest
import uuid
import json


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
        "input": {"name": f"Team {unique_id}", "description": "Test team for import"}
    })
    return result.data["createTeam"]["id"]


def create_export_json(name: str, keys_count: int = 5) -> dict:
    """Create a valid export JSON structure for import testing."""
    keys = []
    locales_en = {}
    locales_ru = {}
    
    for i in range(keys_count):
        key_name = f"test.key.{i}"
        keys.append({
            "key": key_name,
            "description": f"Description for key {i}",
            "tags": ["test"]
        })
        locales_en[key_name] = f"English value {i}"
        locales_ru[key_name] = f"Русское значение {i}"
    
    return {
        "name": name,
        "config": {
            "description": "Imported project",
            "languages": [
                {"code": "en", "locale": "en-US", "direction": "ltr"},
                {"code": "ru", "locale": "ru-RU", "direction": "ltr"}
            ],
            "defaultLanguage": "en",
            "color": "#10b981",
            "status": "active",
            "availableTags": ["test"]
        },
        "keys": keys,
        "locales": [
            {"code": "en", "keys": locales_en},
            {"code": "ru", "keys": locales_ru}
        ]
    }


# ============================================================================
# Import Tests
# ============================================================================

class TestProjectImport:
    """Tests for project import REST API."""

    @pytest.mark.asyncio
    async def test_import_creates_project(self, authenticated_graphql_client):
        """Test that import creates a new project with keys."""
        import httpx
        
        team_id = await create_team(authenticated_graphql_client)
        unique_id = uuid.uuid4().hex[:8]
        
        export_data = create_export_json(f"ImportTest {unique_id}", keys_count=10)
        
        # Import via REST API
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                "http://localhost:8000/api/projects/import",
                headers={"Authorization": f"Bearer {authenticated_graphql_client._token}"},
                data={"team_id": team_id},
                files={"file": ("test_export.json", json.dumps(export_data).encode(), "application/json")},
                timeout=60.0
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "project_id" in data
        assert data["name"] == f"ImportTest {unique_id}"

    @pytest.mark.asyncio
    async def test_import_creates_keys_batch_import_log(self, authenticated_graphql_client):
        """Test that import creates KEYS_BATCH_IMPORT activity log with statistics."""
        import httpx
        
        team_id = await create_team(authenticated_graphql_client)
        unique_id = uuid.uuid4().hex[:8]
        keys_count = 15
        
        export_data = create_export_json(f"ImportLogTest {unique_id}", keys_count=keys_count)
        
        # Import via REST API
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                "http://localhost:8000/api/projects/import",
                headers={"Authorization": f"Bearer {authenticated_graphql_client._token}"},
                data={"team_id": team_id},
                files={"file": ("test_export.json", json.dumps(export_data).encode(), "application/json")},
                timeout=60.0
            )
        
        assert response.status_code == 200
        project_id = response.json()["project_id"]
        
        # Check activity log for KEYS_BATCH_IMPORT
        query = """
            query ProjectActivity($projectId: String!) {
                projectActivity(projectId: $projectId) {
                    id
                    action
                    extraData
                }
            }
        """
        result = await authenticated_graphql_client.execute_async(query, {
            "projectId": project_id
        })
        
        assert result.errors is None, f"GraphQL errors: {result.errors}"
        
        # Find KEYS_BATCH_IMPORT log
        batch_import_logs = [
            log for log in result.data["projectActivity"] 
            if log["action"] == "KEYS_BATCH_IMPORT"
        ]
        
        assert len(batch_import_logs) >= 1, f"KEYS_BATCH_IMPORT log should be created"
        
        # Verify extraData contains statistics
        extra_data = batch_import_logs[0]["extraData"]
        assert extra_data is not None, "extraData should not be null"
        assert extra_data.get("created_keys") == keys_count
        assert extra_data.get("translations_count") == keys_count * 2  # 2 languages

    @pytest.mark.asyncio
    async def test_import_shows_in_team_activity(self, authenticated_graphql_client):
        """Test that import activity shows in team activity log."""
        import httpx
        
        team_id = await create_team(authenticated_graphql_client)
        unique_id = uuid.uuid4().hex[:8]
        
        export_data = create_export_json(f"TeamActivityTest {unique_id}", keys_count=5)
        
        # Import via REST API
        async with httpx.AsyncClient() as http_client:
            await http_client.post(
                "http://localhost:8000/api/projects/import",
                headers={"Authorization": f"Bearer {authenticated_graphql_client._token}"},
                data={"team_id": team_id},
                files={"file": ("test_export.json", json.dumps(export_data).encode(), "application/json")},
                timeout=60.0
            )
        
        # Check team activity log
        query = """
            query TeamActivity($teamId: String!) {
                teamActivity(teamId: $teamId) {
                    id
                    action
                    extraData
                    project {
                        name
                    }
                }
            }
        """
        result = await authenticated_graphql_client.execute_async(query, {
            "teamId": team_id
        })
        
        assert result.errors is None
        
        # Should have KEYS_BATCH_IMPORT in team activity
        actions = [log["action"] for log in result.data["teamActivity"]]
        assert "KEYS_BATCH_IMPORT" in actions, f"Expected KEYS_BATCH_IMPORT in {actions}"

    @pytest.mark.asyncio
    async def test_import_unauthenticated_fails(self):
        """Test that import fails without authentication."""
        import httpx
        
        fake_team_id = str(uuid.uuid4())
        export_data = create_export_json("Unauthenticated Import")
        
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                "http://localhost:8000/api/projects/import",
                data={"team_id": fake_team_id},
                files={"file": ("test.json", json.dumps(export_data).encode(), "application/json")},
                timeout=30.0
            )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_import_invalid_json_fails(self, authenticated_graphql_client):
        """Test that import fails with invalid JSON."""
        import httpx
        
        team_id = await create_team(authenticated_graphql_client)
        
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                "http://localhost:8000/api/projects/import",
                headers={"Authorization": f"Bearer {authenticated_graphql_client._token}"},
                data={"team_id": team_id},
                files={"file": ("test.json", b"not valid json", "application/json")},
                timeout=30.0
            )
        
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_import_missing_name_fails(self, authenticated_graphql_client):
        """Test that import fails when project name is missing."""
        import httpx
        
        team_id = await create_team(authenticated_graphql_client)
        
        export_data = {"config": {}, "keys": [], "locales": []}  # Missing name
        
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                "http://localhost:8000/api/projects/import",
                headers={"Authorization": f"Bearer {authenticated_graphql_client._token}"},
                data={"team_id": team_id},
                files={"file": ("test.json", json.dumps(export_data).encode(), "application/json")},
                timeout=30.0
            )
        
        assert response.status_code == 400

