"""
Integration tests for GraphQL Activity API.
Tests run against http://localhost:8000/graphql
"""
import pytest
import uuid


async def create_team(client) -> str:
    """Helper to create a team."""
    unique_id = uuid.uuid4().hex[:8]
    query = """
        mutation CreateTeam($input: CreateTeamInput!) {
            createTeam(input: $input) { id }
        }
    """
    result = await client.execute_async(query, {
        "input": {"name": f"Team {unique_id}", "description": "Test"}
    })
    return result.data["createTeam"]["id"]


async def create_project(client, team_id: str) -> str:
    """Helper to create a project."""
    unique_id = uuid.uuid4().hex[:8]
    query = """
        mutation CreateProject($input: CreateProjectInput!) {
            createProject(input: $input) { id }
        }
    """
    result = await client.execute_async(query, {
        "input": {
            "name": f"Project {unique_id}",
            "description": "Test",
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
    return result.data["createProject"]["id"]


async def create_key(client, project_id: str) -> str:
    """Helper to create a key."""
    unique_id = uuid.uuid4().hex[:8]
    query = """
        mutation CreateKey($input: CreateKeyInput!) {
            createKey(input: $input) { id }
        }
    """
    result = await client.execute_async(query, {
        "input": {
            "projectId": project_id,
            "key": f"test.key.{unique_id}",
            "description": "Test key",
            "translations": {"en": "Test value", "ru": "Тест"}
        }
    })
    return result.data["createKey"]["id"]


class TestKeyLogsQuery:
    """Tests for keyLogs query."""

    @pytest.mark.asyncio
    async def test_key_logs_returns_history(self, authenticated_graphql_client):
        """Test keyLogs query returns key history."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        key_id = await create_key(authenticated_graphql_client, project_id)
        
        # Make some changes
        await authenticated_graphql_client.execute_async("""
            mutation SetTranslation($input: SetTranslationInput!) {
                setTranslation(input: $input) { id }
            }
        """, {
            "input": {
                "keyId": key_id,
                "language": "en",
                "value": "Updated value"
            }
        })
        
        # Query logs
        query = """
            query KeyLogs($keyId: String!) {
                keyLogs(keyId: $keyId) {
                    id
                    action
                    fieldName
                    oldValue
                    newValue
                    user {
                        username
                    }
                    createdAt
                }
            }
        """
        result = await authenticated_graphql_client.execute_async(query, {"keyId": key_id})
        
        assert result.errors is None
        assert len(result.data["keyLogs"]) >= 1


class TestProjectActivityQuery:
    """Tests for projectActivity query."""

    @pytest.mark.asyncio
    async def test_project_activity_returns_logs(self, authenticated_graphql_client):
        """Test projectActivity query returns activity logs."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        await create_key(authenticated_graphql_client, project_id)
        
        query = """
            query ProjectActivity($projectId: String!, $limit: Int) {
                projectActivity(projectId: $projectId, limit: $limit) {
                    id
                    action
                    user {
                        username
                    }
                }
            }
        """
        result = await authenticated_graphql_client.execute_async(query, {
            "projectId": project_id,
            "limit": 10
        })
        
        assert result.errors is None
        assert len(result.data["projectActivity"]) >= 1

    @pytest.mark.asyncio
    async def test_project_activity_unauthenticated(self, graphql_client):
        """Test projectActivity fails when not authenticated."""
        query = """
            query ProjectActivity($projectId: String!) {
                projectActivity(projectId: $projectId) {
                    id
                }
            }
        """
        result = await graphql_client.execute_async(query, {
            "projectId": "00000000-0000-0000-0000-000000000000"
        })
        
        # Should fail - either errors or null data
        assert result.errors is not None or result.data is None or result.data.get("projectActivity") is None


class TestTeamActivityQuery:
    """Tests for teamActivity query."""

    @pytest.mark.asyncio
    async def test_team_activity_returns_logs(self, authenticated_graphql_client):
        """Test teamActivity query returns activity logs."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        await create_key(authenticated_graphql_client, project_id)
        
        query = """
            query TeamActivity($teamId: String!, $limit: Int) {
                teamActivity(teamId: $teamId, limit: $limit) {
                    id
                    action
                    user {
                        username
                    }
                }
            }
        """
        result = await authenticated_graphql_client.execute_async(query, {
            "teamId": team_id,
            "limit": 10
        })
        
        assert result.errors is None
        assert len(result.data["teamActivity"]) >= 1

    @pytest.mark.asyncio
    async def test_team_activity_unauthenticated(self, graphql_client):
        """Test teamActivity fails when not authenticated."""
        query = """
            query TeamActivity($teamId: String!) {
                teamActivity(teamId: $teamId) {
                    id
                }
            }
        """
        result = await graphql_client.execute_async(query, {
            "teamId": "00000000-0000-0000-0000-000000000000"
        })
        
        # Should fail - either errors or null data
        assert result.errors is not None or result.data is None or result.data.get("teamActivity") is None

    @pytest.mark.asyncio
    async def test_team_activity_includes_extra_data(self, authenticated_graphql_client):
        """Test teamActivity returns extraData field."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        
        query = """
            query TeamActivity($teamId: String!) {
                teamActivity(teamId: $teamId) {
                    id
                    action
                    extraData
                }
            }
        """
        result = await authenticated_graphql_client.execute_async(query, {
            "teamId": team_id
        })
        
        assert result.errors is None, f"GraphQL errors: {result.errors}"
        # extraData field should be queryable (may be null for some actions)
        for log in result.data["teamActivity"]:
            assert "extraData" in log

    @pytest.mark.asyncio
    async def test_team_activity_includes_project_info(self, authenticated_graphql_client):
        """Test teamActivity returns project information."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        
        query = """
            query TeamActivity($teamId: String!) {
                teamActivity(teamId: $teamId) {
                    id
                    action
                    project {
                        id
                        name
                        color
                    }
                }
            }
        """
        result = await authenticated_graphql_client.execute_async(query, {
            "teamId": team_id
        })
        
        assert result.errors is None
        # Should have at least one log with project info
        logs_with_project = [log for log in result.data["teamActivity"] if log["project"]]
        assert len(logs_with_project) >= 1
