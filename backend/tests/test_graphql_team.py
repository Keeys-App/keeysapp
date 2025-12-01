"""
Integration tests for GraphQL Team API.
Tests run against http://localhost:8000/graphql
"""
import pytest
import uuid


class TestTeamsQuery:
    """Tests for teams query."""

    @pytest.mark.asyncio
    async def test_teams_returns_user_teams(self, authenticated_graphql_client):
        """Test teams query returns user's teams."""
        # First create a team
        create_query = """
            mutation CreateTeam($input: CreateTeamInput!) {
                createTeam(input: $input) {
                    id
                    name
                }
            }
        """
        unique_id = uuid.uuid4().hex[:8]
        await authenticated_graphql_client.execute_async(create_query, {
            "input": {
                "name": f"Test Team {unique_id}",
                "description": "Test description"
            }
        })
        
        # Then query teams
        query = """
            query Teams {
                teams {
                    id
                    name
                    description
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query)
        
        assert result.errors is None
        assert len(result.data["teams"]) >= 1

    @pytest.mark.asyncio
    async def test_teams_unauthenticated(self, graphql_client):
        """Test teams query fails when not authenticated."""
        query = """
            query Teams {
                teams {
                    id
                    name
                }
            }
        """
        
        result = await graphql_client.execute_async(query)
        
        # Should fail - either errors or null data
        assert result.errors is not None or result.data is None or result.data.get("teams") is None


class TestTeamQuery:
    """Tests for team query."""

    @pytest.mark.asyncio
    async def test_team_by_id(self, authenticated_graphql_client):
        """Test fetching team by ID."""
        # Create a team
        create_query = """
            mutation CreateTeam($input: CreateTeamInput!) {
                createTeam(input: $input) {
                    id
                    name
                }
            }
        """
        unique_id = uuid.uuid4().hex[:8]
        create_result = await authenticated_graphql_client.execute_async(create_query, {
            "input": {
                "name": f"Team {unique_id}",
                "description": "Test"
            }
        })
        
        team_id = create_result.data["createTeam"]["id"]
        
        # Fetch by ID
        query = """
            query Team($id: String!) {
                team(id: $id) {
                    id
                    name
                    description
                    owner {
                        username
                    }
                    members {
                        user {
                            username
                        }
                        role
                    }
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {"id": team_id})
        
        assert result.errors is None
        assert result.data["team"]["id"] == team_id

    @pytest.mark.asyncio
    async def test_team_not_found(self, authenticated_graphql_client):
        """Test fetching nonexistent team."""
        query = """
            query Team($id: String!) {
                team(id: $id) {
                    id
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "id": "00000000-0000-0000-0000-000000000000"
        })
        
        assert result.data["team"] is None


class TestCreateTeamMutation:
    """Tests for createTeam mutation."""

    @pytest.mark.asyncio
    async def test_create_team_success(self, authenticated_graphql_client):
        """Test successful team creation."""
        unique_id = uuid.uuid4().hex[:8]
        
        query = """
            mutation CreateTeam($input: CreateTeamInput!) {
                createTeam(input: $input) {
                    id
                    name
                    description
                    owner {
                        id
                    }
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "name": f"New Team {unique_id}",
                "description": "A new team"
            }
        })
        
        assert result.errors is None
        assert result.data["createTeam"]["name"] == f"New Team {unique_id}"
        assert result.data["createTeam"]["owner"]["id"] == authenticated_graphql_client.test_user["id"]

    @pytest.mark.asyncio
    async def test_create_team_unauthenticated(self, graphql_client):
        """Test team creation fails when not authenticated."""
        query = """
            mutation CreateTeam($input: CreateTeamInput!) {
                createTeam(input: $input) {
                    id
                }
            }
        """
        
        result = await graphql_client.execute_async(query, {
            "input": {
                "name": "Should Fail",
                "description": "Test"
            }
        })
        
        assert result.errors is not None or result.data["createTeam"] is None


class TestUpdateTeamMutation:
    """Tests for updateTeam mutation."""

    @pytest.mark.asyncio
    async def test_update_team_success(self, authenticated_graphql_client):
        """Test successful team update."""
        # Create team
        create_query = """
            mutation CreateTeam($input: CreateTeamInput!) {
                createTeam(input: $input) {
                    id
                }
            }
        """
        unique_id = uuid.uuid4().hex[:8]
        create_result = await authenticated_graphql_client.execute_async(create_query, {
            "input": {"name": f"Original {unique_id}", "description": "Test"}
        })
        team_id = create_result.data["createTeam"]["id"]
        
        # Update team
        update_query = """
            mutation UpdateTeam($input: UpdateTeamInput!) {
                updateTeam(input: $input) {
                    id
                    name
                    description
                }
            }
        """
        new_name = f"Updated {unique_id}"
        result = await authenticated_graphql_client.execute_async(update_query, {
            "input": {
                "id": team_id,
                "name": new_name,
                "description": "Updated description"
            }
        })
        
        assert result.errors is None
        assert result.data["updateTeam"]["name"] == new_name


class TestDeleteTeamMutation:
    """Tests for deleteTeam mutation."""

    @pytest.mark.asyncio
    async def test_delete_team_success(self, authenticated_graphql_client):
        """Test successful team deletion."""
        # Create team
        create_query = """
            mutation CreateTeam($input: CreateTeamInput!) {
                createTeam(input: $input) {
                    id
                }
            }
        """
        unique_id = uuid.uuid4().hex[:8]
        create_result = await authenticated_graphql_client.execute_async(create_query, {
            "input": {"name": f"ToDelete {unique_id}", "description": "Test"}
        })
        team_id = create_result.data["createTeam"]["id"]
        
        # Delete team
        delete_query = """
            mutation DeleteTeam($id: String!) {
                deleteTeam(id: $id)
            }
        """
        result = await authenticated_graphql_client.execute_async(delete_query, {"id": team_id})
        
        assert result.errors is None
        assert result.data["deleteTeam"] is True
        
        # Verify deleted
        query = """
            query Team($id: String!) {
                team(id: $id) { id }
            }
        """
        verify_result = await authenticated_graphql_client.execute_async(query, {"id": team_id})
        assert verify_result.data["team"] is None


class TestAddTeamMemberMutation:
    """Tests for addTeamMember mutation."""

    @pytest.mark.asyncio
    async def test_add_nonexistent_user_creates_invitation(self, authenticated_graphql_client):
        """Test adding nonexistent user creates invitation."""
        # Create team
        create_query = """
            mutation CreateTeam($input: CreateTeamInput!) {
                createTeam(input: $input) {
                    id
                }
            }
        """
        unique_id = uuid.uuid4().hex[:8]
        create_result = await authenticated_graphql_client.execute_async(create_query, {
            "input": {"name": f"InviteTeam {unique_id}", "description": "Test"}
        })
        team_id = create_result.data["createTeam"]["id"]
        
        # Add nonexistent user (should create invitation)
        add_query = """
            mutation AddTeamMember($input: AddTeamMemberInput!) {
                addTeamMember(input: $input) {
                    id
                }
            }
        """
        result = await authenticated_graphql_client.execute_async(add_query, {
            "input": {
                "teamId": team_id,
                "userEmail": f"nonexistent_{unique_id}@example.com",
                "role": "viewer"
            }
        })
        
        # Should succeed (creates invitation)
        assert result.errors is None


class TestInviteInfoQuery:
    """Tests for inviteInfo query."""

    @pytest.mark.asyncio
    async def test_invite_info_invalid_code(self, graphql_client):
        """Test inviteInfo with invalid code."""
        query = """
            query InviteInfo($code: String!) {
                inviteInfo(code: $code) {
                    teamName
                    inviterName
                    email
                }
            }
        """
        
        result = await graphql_client.execute_async(query, {"code": "invalid-code"})
        
        # Should return null or errors for invalid code
        assert result.errors is not None or result.data is None or result.data.get("inviteInfo") is None
