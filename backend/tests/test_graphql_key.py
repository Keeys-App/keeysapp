"""
Integration tests for GraphQL Key API.
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


async def create_key(client, project_id: str, key_name: str = None, is_plural: bool = False) -> str:
    """Helper to create a key."""
    unique_id = uuid.uuid4().hex[:8]
    query = """
        mutation CreateKey($input: CreateKeyInput!) {
            createKey(input: $input) { id }
        }
    """
    input_data = {
        "projectId": project_id,
        "key": key_name or f"test.key.{unique_id}",
        "description": "Test key",
        "tags": ["test"],
        "translations": {"en": "Test value", "es": "Valor de prueba"}
    }
    if is_plural:
        input_data["isPlural"] = is_plural
    
    result = await client.execute_async(query, {"input": input_data})
    return result.data["createKey"]["id"]


class TestProjectKeysQuery:
    """Tests for projectKeys query."""

    @pytest.mark.asyncio
    async def test_project_keys_returns_keys(self, authenticated_graphql_client):
        """Test projectKeys query returns project keys."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        await create_key(authenticated_graphql_client, project_id)
        
        query = """
            query ProjectKeys($projectId: String!) {
                projectKeys(projectId: $projectId) {
                    keys {
                        id
                        key
                        description
                        translations {
                            language
                            value
                        }
                    }
                    totalCount
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {"projectId": project_id})
        
        assert result.errors is None
        assert result.data["projectKeys"]["totalCount"] >= 1
        assert len(result.data["projectKeys"]["keys"]) >= 1

    @pytest.mark.asyncio
    async def test_project_keys_with_search(self, authenticated_graphql_client):
        """Test projectKeys with search filter."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        
        unique_id = uuid.uuid4().hex[:8]
        await create_key(authenticated_graphql_client, project_id, f"unique.{unique_id}.key")
        
        query = """
            query ProjectKeys($projectId: String!, $search: String) {
                projectKeys(projectId: $projectId, search: $search) {
                    keys {
                        key
                    }
                    totalCount
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "projectId": project_id,
            "search": unique_id
        })
        
        assert result.errors is None
        assert result.data["projectKeys"]["totalCount"] >= 1


class TestKeyQuery:
    """Tests for key query."""

    @pytest.mark.asyncio
    async def test_key_by_id(self, authenticated_graphql_client):
        """Test fetching key by ID."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        key_id = await create_key(authenticated_graphql_client, project_id)
        
        query = """
            query Key($id: String!) {
                key(id: $id) {
                    id
                    key
                    description
                    tags
                    isPlural
                    translations {
                        language
                        value
                        reviewStatus
                    }
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {"id": key_id})
        
        assert result.errors is None
        assert result.data["key"]["id"] == key_id
        assert result.data["key"]["isPlural"] is False

    @pytest.mark.asyncio
    async def test_key_by_id_with_plural(self, authenticated_graphql_client):
        """Test fetching plural key by ID."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        key_id = await create_key(authenticated_graphql_client, project_id, is_plural=True)
        
        query = """
            query Key($id: String!) {
                key(id: $id) {
                    id
                    isPlural
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {"id": key_id})
        
        assert result.errors is None
        assert result.data["key"]["isPlural"] is True


class TestCreateKeyMutation:
    """Tests for createKey mutation."""

    @pytest.mark.asyncio
    async def test_create_key_success(self, authenticated_graphql_client):
        """Test successful key creation."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        
        unique_id = uuid.uuid4().hex[:8]
        query = """
            mutation CreateKey($input: CreateKeyInput!) {
                createKey(input: $input) {
                    id
                    key
                    description
                    isPlural
                    translations {
                        language
                        value
                    }
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "projectId": project_id,
                "key": f"button.submit.{unique_id}",
                "description": "Submit button text",
                "tags": ["ui", "button"],
                "translations": {"en": "Submit", "es": "Enviar"}
            }
        })
        
        assert result.errors is None
        assert result.data["createKey"]["key"] == f"button.submit.{unique_id}"
        assert result.data["createKey"]["isPlural"] is False

    @pytest.mark.asyncio
    async def test_create_key_with_plural(self, authenticated_graphql_client):
        """Test creating key with isPlural enabled."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        
        unique_id = uuid.uuid4().hex[:8]
        query = """
            mutation CreateKey($input: CreateKeyInput!) {
                createKey(input: $input) {
                    id
                    key
                    isPlural
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "projectId": project_id,
                "key": f"items.count.{unique_id}",
                "description": "Item count with plural",
                "isPlural": True,
                "translations": {"en": "item", "es": "artículo"}
            }
        })
        
        assert result.errors is None
        assert result.data["createKey"]["isPlural"] is True

    @pytest.mark.asyncio
    async def test_create_key_with_autopilot(self, authenticated_graphql_client):
        """Test key creation with autopilot (AI auto-translation)."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        
        unique_id = uuid.uuid4().hex[:8]
        query = """
            mutation CreateKey($input: CreateKeyInput!) {
                createKey(input: $input) {
                    id
                    key
                    translations {
                        language
                        value
                    }
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "projectId": project_id,
                "key": f"autopilot.test.{unique_id}",
                "description": "Button to submit the form",
                "translations": {"en": "Submit"},
                "autopilot": True
            }
        })
        
        assert result.errors is None
        assert result.data["createKey"]["key"] == f"autopilot.test.{unique_id}"
        
        # Autopilot should have generated translations for other languages
        translations = result.data["createKey"]["translations"]
        languages = [t["language"] for t in translations]
        
        # Should have more than just English (project has en and ru)
        assert "en" in languages
        # Russian should be auto-generated
        assert "ru" in languages
        
        # Check Russian translation exists and is not empty
        ru_translation = next((t for t in translations if t["language"] == "ru"), None)
        assert ru_translation is not None
        assert ru_translation["value"] is not None
        assert len(ru_translation["value"]) > 0

    @pytest.mark.asyncio
    async def test_create_key_unauthenticated(self, graphql_client):
        """Test key creation fails when not authenticated."""
        query = """
            mutation CreateKey($input: CreateKeyInput!) {
                createKey(input: $input) {
                    id
                }
            }
        """
        
        result = await graphql_client.execute_async(query, {
            "input": {
                "projectId": "some-id",
                "key": "test.key",
                "translations": {}
            }
        })
        
        assert result.errors is not None or result.data.get("createKey") is None


class TestUpdateKeyMutation:
    """Tests for updateKey mutation."""

    @pytest.mark.asyncio
    async def test_update_key_success(self, authenticated_graphql_client):
        """Test successful key update."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        key_id = await create_key(authenticated_graphql_client, project_id)
        
        query = """
            mutation UpdateKey($input: UpdateKeyInput!) {
                updateKey(input: $input) {
                    id
                    description
                    tags
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "id": key_id,
                "description": "Updated description",
                "tags": ["updated", "tag"]
            }
        })
        
        assert result.errors is None
        assert result.data["updateKey"]["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_update_key_is_plural(self, authenticated_graphql_client):
        """Test updating key isPlural field."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        key_id = await create_key(authenticated_graphql_client, project_id)
        
        # First enable isPlural
        query = """
            mutation UpdateKey($input: UpdateKeyInput!) {
                updateKey(input: $input) {
                    id
                    isPlural
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "id": key_id,
                "isPlural": True
            }
        })
        
        assert result.errors is None
        assert result.data["updateKey"]["isPlural"] is True
        
        # Then disable isPlural
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "id": key_id,
                "isPlural": False
            }
        })
        
        assert result.errors is None
        assert result.data["updateKey"]["isPlural"] is False


class TestDeleteKeyMutation:
    """Tests for deleteKey mutation."""

    @pytest.mark.asyncio
    async def test_delete_key_success(self, authenticated_graphql_client):
        """Test successful key deletion."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        key_id = await create_key(authenticated_graphql_client, project_id)
        
        query = """
            mutation DeleteKey($id: String!) {
                deleteKey(id: $id)
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {"id": key_id})
        
        assert result.errors is None
        assert result.data["deleteKey"] is True

    @pytest.mark.asyncio
    async def test_delete_key_actually_removes_from_db(self, authenticated_graphql_client):
        """Test that deleted key is actually removed from database."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        key_id = await create_key(authenticated_graphql_client, project_id)
        
        # Verify key exists before deletion
        get_query = """
            query Key($id: String!) {
                key(id: $id) {
                    id
                    key
                }
            }
        """
        result = await authenticated_graphql_client.execute_async(get_query, {"id": key_id})
        assert result.errors is None
        assert result.data["key"] is not None
        assert result.data["key"]["id"] == key_id
        
        # Delete the key
        delete_query = """
            mutation DeleteKey($id: String!) {
                deleteKey(id: $id)
            }
        """
        result = await authenticated_graphql_client.execute_async(delete_query, {"id": key_id})
        assert result.errors is None
        assert result.data["deleteKey"] is True
        
        # Verify key no longer exists
        result = await authenticated_graphql_client.execute_async(get_query, {"id": key_id})
        # Should either have errors or return None
        assert result.data is None or result.data.get("key") is None


class TestSetTranslationMutation:
    """Tests for setTranslation mutation."""

    @pytest.mark.asyncio
    async def test_set_translation_new(self, authenticated_graphql_client):
        """Test setting a new translation."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        key_id = await create_key(authenticated_graphql_client, project_id)
        
        query = """
            mutation SetTranslation($input: SetTranslationInput!) {
                setTranslation(input: $input) {
                    language
                    value
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "keyId": key_id,
                "language": "de",
                "value": "Testübersetzung"
            }
        })
        
        assert result.errors is None
        assert result.data["setTranslation"]["language"] == "de"
        assert result.data["setTranslation"]["value"] == "Testübersetzung"

    @pytest.mark.asyncio
    async def test_set_translation_empty_deletes(self, authenticated_graphql_client):
        """Test that setting empty value deletes the translation."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        key_id = await create_key(authenticated_graphql_client, project_id)
        
        # Verify translation exists (created with key)
        get_query = """
            query Key($id: String!) {
                key(id: $id) {
                    translations {
                        language
                        value
                    }
                }
            }
        """
        result = await authenticated_graphql_client.execute_async(get_query, {"id": key_id})
        assert result.errors is None
        en_translation = next(
            (t for t in result.data["key"]["translations"] if t["language"] == "en"), 
            None
        )
        assert en_translation is not None
        assert en_translation["value"] == "Test value"
        
        # Delete translation by setting empty value
        set_query = """
            mutation SetTranslation($input: SetTranslationInput!) {
                setTranslation(input: $input) {
                    language
                    value
                }
            }
        """
        result = await authenticated_graphql_client.execute_async(set_query, {
            "input": {
                "keyId": key_id,
                "language": "en",
                "value": ""
            }
        })
        
        # Should return null for deleted translation
        assert result.errors is None
        assert result.data["setTranslation"] is None
        
        # Verify translation is actually removed
        result = await authenticated_graphql_client.execute_async(get_query, {"id": key_id})
        assert result.errors is None
        en_translation = next(
            (t for t in result.data["key"]["translations"] if t["language"] == "en"), 
            None
        )
        assert en_translation is None, "Translation should be deleted but still exists"

    @pytest.mark.asyncio
    async def test_set_translation_update_existing(self, authenticated_graphql_client):
        """Test updating an existing translation."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        key_id = await create_key(authenticated_graphql_client, project_id)
        
        query = """
            mutation SetTranslation($input: SetTranslationInput!) {
                setTranslation(input: $input) {
                    language
                    value
                }
            }
        """
        
        # Update existing "en" translation
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "keyId": key_id,
                "language": "en",
                "value": "Updated value"
            }
        })
        
        assert result.errors is None
        assert result.data["setTranslation"]["value"] == "Updated value"
        
        # Verify it persisted
        get_query = """
            query Key($id: String!) {
                key(id: $id) {
                    translations {
                        language
                        value
                    }
                }
            }
        """
        result = await authenticated_graphql_client.execute_async(get_query, {"id": key_id})
        en_translation = next(
            (t for t in result.data["key"]["translations"] if t["language"] == "en"), 
            None
        )
        assert en_translation["value"] == "Updated value"


class TestApproveTranslationMutation:
    """Tests for approveTranslation mutation."""

    @pytest.mark.asyncio
    async def test_approve_translation_success(self, authenticated_graphql_client):
        """Test approving a translation."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        key_id = await create_key(authenticated_graphql_client, project_id)
        
        query = """
            mutation ApproveTranslation($input: ApproveTranslationInput!) {
                approveTranslation(input: $input) {
                    id
                    translations {
                        language
                        reviewStatus
                    }
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "keyId": key_id,
                "language": "en"
            }
        })
        
        assert result.errors is None
        translations = result.data["approveTranslation"]["translations"]
        en_translation = next((t for t in translations if t["language"] == "en"), None)
        assert en_translation["reviewStatus"] == "APPROVED"


class TestRejectTranslationMutation:
    """Tests for rejectTranslation mutation."""

    @pytest.mark.asyncio
    async def test_reject_translation_success(self, authenticated_graphql_client):
        """Test rejecting a translation."""
        team_id = await create_team(authenticated_graphql_client)
        project_id = await create_project(authenticated_graphql_client, team_id)
        key_id = await create_key(authenticated_graphql_client, project_id)
        
        query = """
            mutation RejectTranslation($input: RejectTranslationInput!) {
                rejectTranslation(input: $input) {
                    id
                    translations {
                        language
                        reviewStatus
                    }
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "keyId": key_id,
                "language": "en",
                "comment": "Needs improvement"
            }
        })
        
        assert result.errors is None
        translations = result.data["rejectTranslation"]["translations"]
        en_translation = next((t for t in translations if t["language"] == "en"), None)
        assert en_translation["reviewStatus"] == "REJECTED"
