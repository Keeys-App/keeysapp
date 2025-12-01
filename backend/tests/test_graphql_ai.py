"""
Integration tests for GraphQL AI API.
Tests run against http://localhost:8000/graphql
"""
import pytest


class TestAITranslateMutation:
    """Tests for aiTranslate mutation."""

    @pytest.mark.asyncio
    async def test_ai_translate_success(self, authenticated_graphql_client):
        """Test successful AI translation."""
        query = """
            mutation AITranslate($input: TranslateInput!) {
                aiTranslate(input: $input) {
                    text
                    success
                    error
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "text": "Hello, world!",
                "targetLanguage": "Spanish",
                "sourceLanguage": "English"
            }
        })
        
        assert result.errors is None
        assert result.data["aiTranslate"]["success"] is True
        assert result.data["aiTranslate"]["text"] is not None
        assert len(result.data["aiTranslate"]["text"]) > 0

    @pytest.mark.asyncio
    async def test_ai_translate_with_context(self, authenticated_graphql_client):
        """Test AI translation with context."""
        query = """
            mutation AITranslate($input: TranslateInput!) {
                aiTranslate(input: $input) {
                    text
                    success
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "text": "Submit",
                "targetLanguage": "Russian",
                "sourceLanguage": "English",
                "context": "Button text for a form submission"
            }
        })
        
        assert result.errors is None
        assert result.data["aiTranslate"]["success"] is True

    @pytest.mark.asyncio
    async def test_ai_translate_unauthenticated(self, graphql_client):
        """Test AI translation fails when not authenticated."""
        query = """
            mutation AITranslate($input: TranslateInput!) {
                aiTranslate(input: $input) {
                    success
                    error
                }
            }
        """
        
        result = await graphql_client.execute_async(query, {
            "input": {
                "text": "Hello",
                "targetLanguage": "Spanish"
            }
        })
        
        assert result.data["aiTranslate"]["success"] is False
        assert result.data["aiTranslate"]["error"] == "Authentication required"

    @pytest.mark.asyncio
    async def test_ai_translate_preserves_variables(self, authenticated_graphql_client):
        """Test AI translation preserves template variables."""
        query = """
            mutation AITranslate($input: TranslateInput!) {
                aiTranslate(input: $input) {
                    text
                    success
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "text": "Hello, {name}! You have {count} messages.",
                "targetLanguage": "Spanish",
                "sourceLanguage": "English"
            }
        })
        
        assert result.errors is None
        assert result.data["aiTranslate"]["success"] is True
        assert "{name}" in result.data["aiTranslate"]["text"]
        assert "{count}" in result.data["aiTranslate"]["text"]


class TestAIRephraseMutation:
    """Tests for aiRephrase mutation."""

    @pytest.mark.asyncio
    async def test_ai_rephrase_success(self, authenticated_graphql_client):
        """Test successful AI rephrasing."""
        query = """
            mutation AIRephrase($input: RephraseInput!) {
                aiRephrase(input: $input) {
                    text
                    success
                    error
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "text": "Click here to continue",
                "language": "English"
            }
        })
        
        assert result.errors is None
        assert result.data["aiRephrase"]["success"] is True
        assert result.data["aiRephrase"]["text"] is not None

    @pytest.mark.asyncio
    async def test_ai_rephrase_unauthenticated(self, graphql_client):
        """Test AI rephrasing fails when not authenticated."""
        query = """
            mutation AIRephrase($input: RephraseInput!) {
                aiRephrase(input: $input) {
                    success
                    error
                }
            }
        """
        
        result = await graphql_client.execute_async(query, {
            "input": {
                "text": "Hello",
                "language": "English"
            }
        })
        
        assert result.data["aiRephrase"]["success"] is False


class TestAIShortenMutation:
    """Tests for aiShorten mutation."""

    @pytest.mark.asyncio
    async def test_ai_shorten_success(self, authenticated_graphql_client):
        """Test successful AI shortening."""
        query = """
            mutation AIShorten($input: ShortenInput!) {
                aiShorten(input: $input) {
                    text
                    success
                    error
                }
            }
        """
        original_text = "Please click the button below to submit your form and complete the registration process"
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "text": original_text,
                "language": "English"
            }
        })
        
        assert result.errors is None
        assert result.data["aiShorten"]["success"] is True
        assert len(result.data["aiShorten"]["text"]) < len(original_text)

    @pytest.mark.asyncio
    async def test_ai_shorten_unauthenticated(self, graphql_client):
        """Test AI shortening fails when not authenticated."""
        query = """
            mutation AIShorten($input: ShortenInput!) {
                aiShorten(input: $input) {
                    success
                    error
                }
            }
        """
        
        result = await graphql_client.execute_async(query, {
            "input": {
                "text": "Long text here",
                "language": "English"
            }
        })
        
        assert result.data["aiShorten"]["success"] is False


class TestAISuggestVariantsMutation:
    """Tests for aiSuggestVariants mutation."""

    @pytest.mark.asyncio
    async def test_ai_suggest_variants_success(self, authenticated_graphql_client):
        """Test successful AI variant generation."""
        query = """
            mutation AISuggestVariants($input: SuggestVariantsInput!) {
                aiSuggestVariants(input: $input) {
                    variants
                    success
                    error
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "text": "Thank you",
                "language": "English",
                "count": 3
            }
        })
        
        assert result.errors is None
        assert result.data["aiSuggestVariants"]["success"] is True
        assert len(result.data["aiSuggestVariants"]["variants"]) >= 1

    @pytest.mark.asyncio
    async def test_ai_suggest_variants_unauthenticated(self, graphql_client):
        """Test AI variant generation fails when not authenticated."""
        query = """
            mutation AISuggestVariants($input: SuggestVariantsInput!) {
                aiSuggestVariants(input: $input) {
                    success
                    error
                }
            }
        """
        
        result = await graphql_client.execute_async(query, {
            "input": {
                "text": "Hello",
                "language": "English",
                "count": 3
            }
        })
        
        assert result.data["aiSuggestVariants"]["success"] is False

    @pytest.mark.asyncio
    async def test_ai_suggest_variants_preserves_variables(self, authenticated_graphql_client):
        """Test AI variants preserve template variables."""
        query = """
            mutation AISuggestVariants($input: SuggestVariantsInput!) {
                aiSuggestVariants(input: $input) {
                    variants
                    success
                }
            }
        """
        
        result = await authenticated_graphql_client.execute_async(query, {
            "input": {
                "text": "Hello, {username}!",
                "language": "English",
                "count": 3
            }
        })
        
        assert result.errors is None
        assert result.data["aiSuggestVariants"]["success"] is True
        for variant in result.data["aiSuggestVariants"]["variants"]:
            assert "{username}" in variant
