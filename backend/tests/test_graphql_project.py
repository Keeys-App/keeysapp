"""
Integration tests for GraphQL Project API.
Tests run against http://localhost:8000/graphql
"""
import pytest
import uuid


async def create_team(client, name: str = None) -> str:
    """Helper to create a team and return its ID."""
    unique_id = uuid.uuid4().hex[:8]
    query = """
        mutation CreateTeam($input: CreateTeamInput!) {
            createTeam(input: $input) {
                id
            }
        }
    """
    result = await client.execute_async(query, {
        "input": {
            "name": name or f"Team {unique_id}",
            "description": "Test team"
        }
    })
    return result.data["createTeam"]["id"]


async def create_project(client, team_id: str, name: str = None) -> str:
    """Helper to create a project and return its ID."""
    unique_id = uuid.uuid4().hex[:8]
    query = """
        mutation CreateProject($input: CreateProjectInput!) {
            createProject(input: $input) {
                id
            }
        }
    """
    result = await client.execute_async(query, {
        "input": {
            "name": name or f"Project {unique_id}",
            "description": "Test project",
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


class TestProjectsQuery:
    """Tests for projects query."""

    @pytest.mark.asyncio
    async def test_projects_returns_user_projects(self, authenticated_graphql_client):
        """Test projects query returns user's projects."""
        # Create team and project
        team_id = await create_team(authenticated_graphql_client)
        await create_project(authenticated_graphql_client, team_id)
        
        # Query projects
        query = """
            query Projects {
                projects {
                    id
                    name
                    description
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query)
        
        assert result.errors is None
        assert len(result.data["projects"]) >= 1

    @pytest.mark.asyncio
    async def test_projects_unauthenticated(self, graphql_client):
        """Test projects query fails when not authenticated."""
        query = """
            query Projects {
                projects {
                    id
                }
            }
        """
        
        result = await graphql_client.execute_async(query)
        
        # Should fail - either errors or null data
        assert result.errors is not None or result.data is None or result.data.get("projects") is None


class TestProjectQuery:
    """Tests for project query."""

    @pytest.mark.asyncio
    async def test_project_by_id(self, authenticated_graphql_client):
        """Test fetching project by ID."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        
        query = """
            query Project($id: String!) {
                project(id: $id) {
                    id
                    name
                    description
                    languages {
                        code
                        locale
                    }
                    owner {
                        username
                    }
                    team {
                        id
                    }
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {"id": project_id})
        
        assert result.errors is None
        assert result.data["project"]["id"] == project_id

    @pytest.mark.asyncio
    async def test_project_not_found(self, authenticated_graphql_client):
        """Test fetching nonexistent project."""
        query = """
            query Project($id: String!) {
                project(id: $id) {
                    id
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "id": "00000000-0000-0000-0000-000000000000"
        })
        
        assert result.data["project"] is None


class TestCreateProjectMutation:
    """Tests for createProject mutation."""

    @pytest.mark.asyncio
    async def test_create_project_success(self, authenticated_graphql_client):
        """Test successful project creation."""
        team_id = await create_team(authenticated_graphql_client)
        unique_id = uuid.uuid4().hex[:8]
        
        query = """
            mutation CreateProject($input: CreateProjectInput!) {
                createProject(input: $input) {
                    id
                    name
                    description
                    languages {
                        code
                    }
                    defaultLanguage
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "name": f"New Project {unique_id}",
                "description": "A new project",
                "teamId": team_id,
                "languages": [
                    {"code": "en", "locale": "en-US", "direction": "ltr"}
                ],
                "defaultLanguage": "en",
                "color": "#3b82f6",
                "status": "active"
            }
        })
        
        assert result.errors is None
        assert result.data["createProject"]["name"] == f"New Project {unique_id}"

    @pytest.mark.asyncio
    async def test_create_project_unauthenticated(self, graphql_client):
        """Test project creation fails when not authenticated."""
        query = """
            mutation CreateProject($input: CreateProjectInput!) {
                createProject(input: $input) {
                    id
                }
            }
        """
        
        result = await graphql_client.execute_async(query, {
            "input": {
                "name": "Should Fail",
                "teamId": "some-id",
                "languages": [{"code": "en", "locale": "en-US", "direction": "ltr"}],
                "defaultLanguage": "en",
                "color": "#000",
                "status": "active"
            }
        })
        
        assert result.errors is not None or result.data.get("createProject") is None


class TestUpdateProjectMutation:
    """Tests for updateProject mutation."""

    @pytest.mark.asyncio
    async def test_update_project_success(self, authenticated_graphql_client):
        """Test successful project update."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        
        new_name = f"Updated Project {uuid.uuid4().hex[:8]}"
        query = """
            mutation UpdateProject($input: UpdateProjectInput!) {
                updateProject(input: $input) {
                    id
                    name
                    description
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "id": project_id,
                "name": new_name,
                "description": "Updated description"
            }
        })
        
        assert result.errors is None
        assert result.data["updateProject"]["name"] == new_name


class TestDeleteProjectMutation:
    """Tests for deleteProject mutation."""

    @pytest.mark.asyncio
    async def test_delete_project_success(self, authenticated_graphql_client):
        """Test successful project deletion."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        
        query = """
            mutation DeleteProject($id: String!) {
                deleteProject(id: $id)
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {"id": project_id})
        
        assert result.errors is None
        assert result.data["deleteProject"] is True
        
        # Verify deleted
        verify_query = """
            query Project($id: String!) {
                project(id: $id) { id }
            }
        """
        verify_result = await authenticated_graphql_client.execute_async(verify_query, {"id": project_id})
        assert verify_result.data["project"] is None
