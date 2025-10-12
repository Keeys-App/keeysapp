"""
Tests for AI Service
"""
import pytest
from app.services.ai_service import ai_service


class TestAIServiceValidation:
    """Test AI service response validation"""
    
    @pytest.mark.asyncio
    async def test_translate_valid_text(self):
        """Test translation with valid text"""
        result, reason = await ai_service.translate(
            text="Hello, world!",
            target_language="Spanish",
            source_language="English"
        )
        
        assert result is not None
        assert len(result) > 0
        assert reason is None  # No error reason
        # Should not contain apologies or error messages
        assert "sorry" not in result.lower()
        assert "lo siento" not in result.lower()
        assert "i cannot" not in result.lower()
    
    @pytest.mark.asyncio
    async def test_translate_gibberish(self):
        """Test translation with gibberish - should return reason"""
        result, reason = await ai_service.translate(
            text="asdasdasd",
            target_language="Spanish",
            source_language="English"
        )
        
        # Should return empty result with reason
        assert result == ""
        assert reason is not None
        assert len(reason) > 0
        # Reason should explain the issue
        assert "gibberish" in reason.lower() or "random" in reason.lower() or "unclear" in reason.lower() or "meaning" in reason.lower()
    
    @pytest.mark.asyncio
    async def test_rephrase_valid_text(self):
        """Test rephrasing with valid text"""
        result, reason = await ai_service.rephrase(
            text="This is a test",
            language="English"
        )
        
        assert result is not None
        assert len(result) > 0
        assert reason is None
        assert "sorry" not in result.lower()
    
    @pytest.mark.asyncio
    async def test_rephrase_gibberish(self):
        """Test rephrasing with gibberish - should return reason"""
        result, reason = await ai_service.rephrase(
            text="xyzxyzxyz",
            language="Spanish"
        )
        
        assert result == ""
        assert reason is not None
        assert len(reason) > 0
    
    @pytest.mark.asyncio
    async def test_shorten_valid_text(self):
        """Test shortening with valid text"""
        result, reason = await ai_service.shorten(
            text="This is a very long sentence that needs to be shortened significantly",
            language="English"
        )
        
        assert result is not None
        assert len(result) > 0
        assert reason is None
        assert "sorry" not in result.lower()
    
    @pytest.mark.asyncio
    async def test_suggest_variants_valid_text(self):
        """Test variant generation with valid text"""
        variants, reason = await ai_service.suggest_variants(
            text="Thank you",
            language="English",
            count=3
        )
        
        assert variants is not None
        assert len(variants) >= 1
        assert reason is None
        # All variants should be actual alternatives, not apologies
        for variant in variants:
            assert "sorry" not in variant.lower()
            assert "cannot" not in variant.lower()
    
    @pytest.mark.asyncio
    async def test_suggest_variants_gibberish(self):
        """Test variant generation with gibberish - should return reason"""
        variants, reason = await ai_service.suggest_variants(
            text="qweasdzxc",
            language="French",
            count=3
        )
        
        assert variants == []
        assert reason is not None
        assert len(reason) > 0


class TestAIServiceWithContext:
    """Test AI service with context"""
    
    @pytest.mark.asyncio
    async def test_translate_with_context(self):
        """Test that context affects translation"""
        result, reason = await ai_service.translate(
            text="Welcome",
            target_language="Spanish",
            source_language="English",
            context="Formal greeting for business website"
        )
        
        assert result is not None
        assert len(result) > 0
        assert reason is None
        # Should be formal (e.g., "Bienvenido" not "Hola")
    
    @pytest.mark.asyncio
    async def test_rephrase_with_context(self):
        """Test that context affects rephrasing"""
        result, reason = await ai_service.rephrase(
            text="Click here",
            language="English",
            context="Call-to-action button, should be engaging"
        )
        
        assert result is not None
        assert len(result) > 0
        assert reason is None


class TestAIServiceMultipleLanguages:
    """Test AI service with different languages"""
    
    @pytest.mark.asyncio
    async def test_translate_to_russian(self):
        """Test translation to Russian"""
        result, reason = await ai_service.translate(
            text="Good morning",
            target_language="Russian",
            source_language="English"
        )
        
        assert result is not None
        assert len(result) > 0
        assert reason is None
    
    @pytest.mark.asyncio
    async def test_translate_to_chinese(self):
        """Test translation to Chinese"""
        result, reason = await ai_service.translate(
            text="Thank you",
            target_language="Chinese",
            source_language="English"
        )
        
        assert result is not None
        assert len(result) > 0
        assert reason is None
    
    @pytest.mark.asyncio
    async def test_translate_to_arabic(self):
        """Test translation to Arabic"""
        result, reason = await ai_service.translate(
            text="Welcome",
            target_language="Arabic",
            source_language="English"
        )
        
        assert result is not None
        assert len(result) > 0
        assert reason is None

