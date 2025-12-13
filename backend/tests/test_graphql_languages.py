"""
Integration tests for GraphQL Languages API.
Tests run against http://localhost:8000/graphql

Tests the availableLanguages query and language integration with projects.
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


async def create_project_with_languages(client, team_id: str, languages: list) -> dict:
    """Helper to create a project with specific languages and return full project data."""
    unique_id = uuid.uuid4().hex[:8]
    query = """
        mutation CreateProject($input: CreateProjectInput!) {
            createProject(input: $input) {
                id
                name
                languages {
                    code
                    locale
                    direction
                    pluralForms
                    default
                }
                defaultLanguage
            }
        }
    """
    result = await client.execute_async(query, {
        "input": {
            "name": f"Project {unique_id}",
            "description": "Test project",
            "teamId": team_id,
            "languages": languages,
            "defaultLanguage": languages[0]["code"] if languages else None,
            "color": "#6366f1",
            "status": "active"
        }
    })
    return result.data["createProject"]


class TestAvailableLanguagesQuery:
    """Tests for availableLanguages query."""

    @pytest.mark.asyncio
    async def test_available_languages_returns_all_languages(self, graphql_client):
        """Test availableLanguages query returns list of languages without authentication."""
        query = """
            query AvailableLanguages {
                availableLanguages {
                    code
                    name
                    nativeName
                    flag
                    locale
                    direction
                    pluralForms
                    detectionPatterns {
                        endPatterns
                        middlePatterns
                        startPatterns
                        fullNames
                    }
                }
            }
        """
        
        result = await graphql_client.execute_async(query)
        
        assert result.errors is None
        assert result.data is not None
        languages = result.data["availableLanguages"]
        assert len(languages) > 0
        
        # Check that common languages are present
        codes = [lang["code"] for lang in languages]
        assert "en" in codes
        assert "ru" in codes
        assert "es" in codes
        assert "ar" in codes

    @pytest.mark.asyncio
    async def test_available_languages_structure(self, graphql_client):
        """Test availableLanguages returns correct structure for each language."""
        query = """
            query AvailableLanguages {
                availableLanguages {
                    code
                    name
                    nativeName
                    flag
                    locale
                    direction
                    pluralForms
                    detectionPatterns {
                        endPatterns
                        middlePatterns
                        startPatterns
                        fullNames
                    }
                }
            }
        """
        
        result = await graphql_client.execute_async(query)
        
        assert result.errors is None
        languages = result.data["availableLanguages"]
        
        # Check each language has all required fields
        for lang in languages:
            assert "code" in lang and lang["code"]
            assert "name" in lang and lang["name"]
            assert "nativeName" in lang and lang["nativeName"]
            assert "flag" in lang and lang["flag"]
            assert "locale" in lang and lang["locale"]
            assert "direction" in lang and lang["direction"] in ["ltr", "rtl"]
            assert "pluralForms" in lang and isinstance(lang["pluralForms"], list)
            assert len(lang["pluralForms"]) > 0
            assert "detectionPatterns" in lang
            assert "endPatterns" in lang["detectionPatterns"]
            assert "middlePatterns" in lang["detectionPatterns"]
            assert "startPatterns" in lang["detectionPatterns"]
            assert "fullNames" in lang["detectionPatterns"]

    @pytest.mark.asyncio
    async def test_english_language_details(self, graphql_client):
        """Test English language has correct details."""
        query = """
            query AvailableLanguages {
                availableLanguages {
                    code
                    name
                    nativeName
                    flag
                    locale
                    direction
                    pluralForms
                }
            }
        """
        
        result = await graphql_client.execute_async(query)
        
        assert result.errors is None
        languages = result.data["availableLanguages"]
        english = next((l for l in languages if l["code"] == "en"), None)
        
        assert english is not None
        assert english["name"] == "English"
        assert english["nativeName"] == "English"
        assert english["flag"] == "🇬🇧"
        assert english["locale"] == "en-US"
        assert english["direction"] == "ltr"
        assert english["pluralForms"] == ["one", "other"]

    @pytest.mark.asyncio
    async def test_russian_language_plural_forms(self, graphql_client):
        """Test Russian language has correct plural forms (one/few/many/other)."""
        query = """
            query AvailableLanguages {
                availableLanguages {
                    code
                    name
                    nativeName
                    pluralForms
                }
            }
        """
        
        result = await graphql_client.execute_async(query)
        
        assert result.errors is None
        languages = result.data["availableLanguages"]
        russian = next((l for l in languages if l["code"] == "ru"), None)
        
        assert russian is not None
        assert russian["name"] == "Russian"
        assert russian["nativeName"] == "Russkiy"  # Transliterated
        assert russian["pluralForms"] == ["one", "few", "many", "other"]

    @pytest.mark.asyncio
    async def test_arabic_language_plural_forms(self, graphql_client):
        """Test Arabic language has most complex plural forms (zero/one/two/few/many/other)."""
        query = """
            query AvailableLanguages {
                availableLanguages {
                    code
                    name
                    direction
                    pluralForms
                }
            }
        """
        
        result = await graphql_client.execute_async(query)
        
        assert result.errors is None
        languages = result.data["availableLanguages"]
        arabic = next((l for l in languages if l["code"] == "ar"), None)
        
        assert arabic is not None
        assert arabic["name"] == "Arabic"
        assert arabic["direction"] == "rtl"
        assert arabic["pluralForms"] == ["zero", "one", "two", "few", "many", "other"]

    @pytest.mark.asyncio
    async def test_chinese_language_no_plural_forms(self, graphql_client):
        """Test Chinese language has only 'other' plural form (no plural distinction)."""
        query = """
            query AvailableLanguages {
                availableLanguages {
                    code
                    name
                    pluralForms
                }
            }
        """
        
        result = await graphql_client.execute_async(query)
        
        assert result.errors is None
        languages = result.data["availableLanguages"]
        chinese = next((l for l in languages if l["code"] == "zh"), None)
        
        assert chinese is not None
        assert chinese["name"] == "Chinese"
        assert chinese["pluralForms"] == ["other"]

    @pytest.mark.asyncio
    async def test_detection_patterns_are_valid_regex(self, graphql_client):
        """Test detection patterns are valid regex strings."""
        import re
        
        query = """
            query AvailableLanguages {
                availableLanguages {
                    code
                    detectionPatterns {
                        endPatterns
                        middlePatterns
                        startPatterns
                        fullNames
                    }
                }
            }
        """
        
        result = await graphql_client.execute_async(query)
        
        assert result.errors is None
        languages = result.data["availableLanguages"]
        
        for lang in languages:
            patterns = lang["detectionPatterns"]
            all_patterns = (
                patterns["endPatterns"] + 
                patterns["middlePatterns"] + 
                patterns["startPatterns"] + 
                patterns["fullNames"]
            )
            
            for pattern in all_patterns:
                # Should not raise an exception
                try:
                    re.compile(pattern, re.IGNORECASE)
                except re.error as e:
                    pytest.fail(f"Invalid regex pattern for {lang['code']}: {pattern} - {e}")


class TestProjectLanguagesIntegration:
    """Tests for language integration with projects."""

    @pytest.mark.asyncio
    async def test_project_languages_include_plural_forms(self, authenticated_graphql_client):
        """Test that project languages include plural forms from available languages."""
        team_id = await create_team(authenticated_graphql_client)
        
        project = await create_project_with_languages(
            authenticated_graphql_client,
            team_id,
            [
                {"code": "en", "locale": "en-US", "direction": "ltr"},
                {"code": "ru", "locale": "ru-RU", "direction": "ltr"}
            ]
        )
        
        assert project is not None
        assert len(project["languages"]) == 2
        
        # Find English and Russian in project languages
        en_lang = next((l for l in project["languages"] if l["code"] == "en"), None)
        ru_lang = next((l for l in project["languages"] if l["code"] == "ru"), None)
        
        assert en_lang is not None
        assert en_lang["pluralForms"] == ["one", "other"]
        
        assert ru_lang is not None
        assert ru_lang["pluralForms"] == ["one", "few", "many", "other"]

    @pytest.mark.asyncio
    async def test_project_with_rtl_language(self, authenticated_graphql_client):
        """Test creating project with RTL language (Arabic)."""
        team_id = await create_team(authenticated_graphql_client)
        
        project = await create_project_with_languages(
            authenticated_graphql_client,
            team_id,
            [
                {"code": "en", "locale": "en-US", "direction": "ltr"},
                {"code": "ar", "locale": "ar-SA", "direction": "rtl"}
            ]
        )
        
        assert project is not None
        assert len(project["languages"]) == 2
        
        ar_lang = next((l for l in project["languages"] if l["code"] == "ar"), None)
        
        assert ar_lang is not None
        assert ar_lang["direction"] == "rtl"
        assert ar_lang["pluralForms"] == ["zero", "one", "two", "few", "many", "other"]

    @pytest.mark.asyncio
    async def test_project_default_language_marked(self, authenticated_graphql_client):
        """Test that default language is correctly marked in project."""
        team_id = await create_team(authenticated_graphql_client)
        
        project = await create_project_with_languages(
            authenticated_graphql_client,
            team_id,
            [
                {"code": "en", "locale": "en-US", "direction": "ltr"},
                {"code": "es", "locale": "es-ES", "direction": "ltr"},
                {"code": "fr", "locale": "fr-FR", "direction": "ltr"}
            ]
        )
        
        assert project is not None
        assert project["defaultLanguage"] == "en"
        
        # Check default flag on languages
        for lang in project["languages"]:
            if lang["code"] == "en":
                assert lang["default"] is True
            else:
                assert lang["default"] is False

    @pytest.mark.asyncio
    async def test_project_with_east_asian_languages(self, authenticated_graphql_client):
        """Test project with East Asian languages that have no plural forms."""
        team_id = await create_team(authenticated_graphql_client)
        
        project = await create_project_with_languages(
            authenticated_graphql_client,
            team_id,
            [
                {"code": "en", "locale": "en-US", "direction": "ltr"},
                {"code": "zh", "locale": "zh-CN", "direction": "ltr"},
                {"code": "ja", "locale": "ja-JP", "direction": "ltr"},
                {"code": "ko", "locale": "ko-KR", "direction": "ltr"}
            ]
        )
        
        assert project is not None
        assert len(project["languages"]) == 4
        
        # All East Asian languages should have only "other" plural form
        for code in ["zh", "ja", "ko"]:
            lang = next((l for l in project["languages"] if l["code"] == code), None)
            assert lang is not None
            assert lang["pluralForms"] == ["other"]

    @pytest.mark.asyncio
    async def test_update_project_languages_preserves_plural_forms(self, authenticated_graphql_client):
        """Test that updating project languages preserves plural forms."""
        team_id = await create_team(authenticated_graphql_client)
        
        # Create project with English only
        project = await create_project_with_languages(
            authenticated_graphql_client,
            team_id,
            [{"code": "en", "locale": "en-US", "direction": "ltr"}]
        )
        
        # Update project to add more languages
        update_query = """
            mutation UpdateProject($input: UpdateProjectInput!) {
                updateProject(input: $input) {
                    id
                    languages {
                        code
                        locale
                        direction
                        pluralForms
                    }
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(update_query, {
            "input": {
                "id": project["id"],
                "languages": [
                    {"code": "en", "locale": "en-US", "direction": "ltr"},
                    {"code": "ru", "locale": "ru-RU", "direction": "ltr"},
                    {"code": "pl", "locale": "pl-PL", "direction": "ltr"}
                ]
            }
        })
        
        assert result.errors is None
        updated_project = result.data["updateProject"]
        assert len(updated_project["languages"]) == 3
        
        # All Slavic languages should have 4 plural forms
        ru_lang = next((l for l in updated_project["languages"] if l["code"] == "ru"), None)
        pl_lang = next((l for l in updated_project["languages"] if l["code"] == "pl"), None)
        
        assert ru_lang["pluralForms"] == ["one", "few", "many", "other"]
        assert pl_lang["pluralForms"] == ["one", "few", "many", "other"]


class TestLanguageConsistency:
    """Tests for consistency between availableLanguages and project languages."""

    @pytest.mark.asyncio
    async def test_project_language_plural_forms_match_available(self, authenticated_graphql_client, graphql_client):
        """Test that plural forms in project match those from availableLanguages."""
        # Get available languages
        available_query = """
            query AvailableLanguages {
                availableLanguages {
                    code
                    pluralForms
                }
            }
        """
        available_result = await graphql_client.execute_async(available_query)
        available_languages = {
            lang["code"]: lang["pluralForms"] 
            for lang in available_result.data["availableLanguages"]
        }
        
        # Create project with multiple languages
        team_id = await create_team(authenticated_graphql_client)
        project = await create_project_with_languages(
            authenticated_graphql_client,
            team_id,
            [
                {"code": "en", "locale": "en-US", "direction": "ltr"},
                {"code": "ru", "locale": "ru-RU", "direction": "ltr"},
                {"code": "ar", "locale": "ar-SA", "direction": "rtl"},
                {"code": "zh", "locale": "zh-CN", "direction": "ltr"}
            ]
        )
        
        # Verify each project language has matching plural forms
        for lang in project["languages"]:
            code = lang["code"]
            assert code in available_languages
            assert lang["pluralForms"] == available_languages[code], \
                f"Plural forms mismatch for {code}: {lang['pluralForms']} != {available_languages[code]}"

    @pytest.mark.asyncio
    async def test_all_available_languages_can_be_used_in_project(self, authenticated_graphql_client, graphql_client):
        """Test that any language from availableLanguages can be added to a project."""
        # Get all available languages
        available_query = """
            query AvailableLanguages {
                availableLanguages {
                    code
                    locale
                    direction
                }
            }
        """
        available_result = await graphql_client.execute_async(available_query)
        available_languages = available_result.data["availableLanguages"]
        
        team_id = await create_team(authenticated_graphql_client)
        
        # Create project with ALL available languages
        languages_input = [
            {"code": lang["code"], "locale": lang["locale"], "direction": lang["direction"]}
            for lang in available_languages
        ]
        
        project = await create_project_with_languages(
            authenticated_graphql_client,
            team_id,
            languages_input
        )
        
        assert project is not None
        assert len(project["languages"]) == len(available_languages)
        
        # Verify all languages are present
        project_codes = {lang["code"] for lang in project["languages"]}
        available_codes = {lang["code"] for lang in available_languages}
        assert project_codes == available_codes

