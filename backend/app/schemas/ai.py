"""
GraphQL schemas for AI operations
"""
import strawberry
from typing import Optional
from strawberry.types import Info
from app.services.ai_service import ai_service
from app.schemas.project import get_current_user_id
import logging

logger = logging.getLogger(__name__)


@strawberry.type
class TranslationResult:
    """Result of a translation operation"""
    text: str
    success: bool
    error: Optional[str] = None


@strawberry.type
class VariantsResult:
    """Result of a variants generation operation"""
    variants: list[str]
    success: bool
    error: Optional[str] = None


@strawberry.input
class TranslateInput:
    """Input for translation operation"""
    text: str
    target_language: str
    source_language: Optional[str] = None
    context: Optional[str] = None


@strawberry.input
class RephraseInput:
    """Input for rephrase operation"""
    text: str
    language: str
    context: Optional[str] = None


@strawberry.input
class ShortenInput:
    """Input for shorten operation"""
    text: str
    language: str
    context: Optional[str] = None


@strawberry.input
class SuggestVariantsInput:
    """Input for suggest variants operation"""
    text: str
    language: str
    context: Optional[str] = None
    count: Optional[int] = 3


@strawberry.type
class AIMutation:
    """AI operations mutations"""

    @strawberry.mutation
    async def ai_translate(
        self,
        info: Info,
        input: TranslateInput
    ) -> TranslationResult:
        """
        Translate text using AI
        
        Requires authentication.
        """
        try:
            # Check authentication
            user_id = get_current_user_id(info)
            if not user_id:
                return TranslationResult(
                    text="",
                    success=False,
                    error="Authentication required"
                )

            logger.info(f"User {user_id} requesting AI translation")

            # Perform translation
            translated_text = await ai_service.translate(
                text=input.text,
                target_language=input.target_language,
                source_language=input.source_language,
                context=input.context
            )

            return TranslationResult(
                text=translated_text,
                success=True
            )

        except Exception as e:
            logger.error(f"AI translation error: {str(e)}")
            return TranslationResult(
                text="",
                success=False,
                error="Translation failed. Please try again."
            )

    @strawberry.mutation
    async def ai_rephrase(
        self,
        info: Info,
        input: RephraseInput
    ) -> TranslationResult:
        """
        Rephrase text using AI
        
        Requires authentication.
        """
        try:
            # Check authentication
            user_id = get_current_user_id(info)
            if not user_id:
                return TranslationResult(
                    text="",
                    success=False,
                    error="Authentication required"
                )

            logger.info(f"User {user_id} requesting AI rephrase")

            # Perform rephrase
            rephrased_text = await ai_service.rephrase(
                text=input.text,
                language=input.language,
                context=input.context
            )

            return TranslationResult(
                text=rephrased_text,
                success=True
            )

        except Exception as e:
            logger.error(f"AI rephrase error: {str(e)}")
            return TranslationResult(
                text="",
                success=False,
                error="Rephrase failed. Please try again."
            )

    @strawberry.mutation
    async def ai_shorten(
        self,
        info: Info,
        input: ShortenInput
    ) -> TranslationResult:
        """
        Shorten text using AI
        
        Requires authentication.
        """
        try:
            # Check authentication
            user_id = get_current_user_id(info)
            if not user_id:
                return TranslationResult(
                    text="",
                    success=False,
                    error="Authentication required"
                )

            logger.info(f"User {user_id} requesting AI shorten")

            # Perform shorten
            shortened_text = await ai_service.shorten(
                text=input.text,
                language=input.language,
                context=input.context
            )

            return TranslationResult(
                text=shortened_text,
                success=True
            )

        except Exception as e:
            logger.error(f"AI shorten error: {str(e)}")
            return TranslationResult(
                text="",
                success=False,
                error="Shorten failed. Please try again."
            )

    @strawberry.mutation
    async def ai_suggest_variants(
        self,
        info: Info,
        input: SuggestVariantsInput
    ) -> VariantsResult:
        """
        Generate text variants using AI
        
        Requires authentication.
        """
        try:
            # Check authentication
            user_id = get_current_user_id(info)
            if not user_id:
                return VariantsResult(
                    variants=[],
                    success=False,
                    error="Authentication required"
                )

            logger.info(f"User {user_id} requesting AI variants")

            # Generate variants
            variants = await ai_service.suggest_variants(
                text=input.text,
                language=input.language,
                context=input.context,
                count=input.count or 3
            )

            return VariantsResult(
                variants=variants,
                success=True
            )

        except Exception as e:
            logger.error(f"AI variants error: {str(e)}")
            return VariantsResult(
                variants=[],
                success=False,
                error="Variant generation failed. Please try again."
            )

