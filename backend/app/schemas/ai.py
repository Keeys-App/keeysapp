"""
GraphQL schemas for AI operations
"""
import strawberry
from typing import Optional, List
from strawberry.types import Info
from sqlalchemy import select
from app.services.ai_service import ai_service, get_available_models
from app.services.token_usage_service import TokenUsageService
from app.schemas.project import get_current_user_id
from app.database import AsyncSessionLocal
from app.services.team_service import TeamService
from app.models.team import Team
import logging

logger = logging.getLogger(__name__)


async def get_team_ai_settings(team_id: str) -> tuple[Optional[str], Optional[str]]:
    """
    Get AI settings for a team.
    
    Args:
        team_id: Team UUID
        
    Returns:
        Tuple of (ai_provider, ai_model)
    """
    async with AsyncSessionLocal() as db:
        team = await TeamService.get_team_by_public_id(db, team_id)
        if team:
            return (team.ai_provider, team.ai_model)
        return (None, None)


@strawberry.type
class TranslationResult:
    """Result of a translation operation"""
    text: str
    success: bool
    error: Optional[str] = None
    reason: Optional[str] = None  # AI's explanation when it cannot process


@strawberry.type
class VariantsResult:
    """Result of a variants generation operation"""
    variants: list[str]
    success: bool
    error: Optional[str] = None
    reason: Optional[str] = None  # AI's explanation when it cannot process


@strawberry.input
class TranslateInput:
    """Input for translation operation"""
    text: str
    target_language: str
    source_language: Optional[str] = None
    context: Optional[str] = None
    team_id: Optional[str] = None  # Team UUID to use team's AI settings


@strawberry.input
class RephraseInput:
    """Input for rephrase operation"""
    text: str
    language: str
    context: Optional[str] = None
    team_id: Optional[str] = None  # Team UUID to use team's AI settings


@strawberry.input
class ShortenInput:
    """Input for shorten operation"""
    text: str
    language: str
    context: Optional[str] = None
    team_id: Optional[str] = None  # Team UUID to use team's AI settings


@strawberry.input
class SuggestVariantsInput:
    """Input for suggest variants operation"""
    text: str
    language: str
    context: Optional[str] = None
    count: Optional[int] = 3
    team_id: Optional[str] = None  # Team UUID to use team's AI settings


@strawberry.type
class AIModelInfo:
    """Information about an available AI model"""
    id: str
    name: str
    description: str


@strawberry.type
class AIProviderModels:
    """Available models for an AI provider"""
    provider: str
    models: List[AIModelInfo]


@strawberry.type
class AIQuery:
    """AI operations queries"""

    @strawberry.field
    async def available_ai_models(self, info: Info) -> List[AIProviderModels]:
        """
        Get available AI models for all providers.
        
        Requires authentication.
        """
        # Check authentication
        user_id = await get_current_user_id(info)
        if not user_id:
            return []

        models = get_available_models()
        result = []
        for provider, provider_models in models.items():
            result.append(AIProviderModels(
                provider=provider,
                models=[
                    AIModelInfo(
                        id=m["id"],
                        name=m["name"],
                        description=m["description"]
                    )
                    for m in provider_models
                ]
            ))
        return result


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
            user_id = await get_current_user_id(info)
            if not user_id:
                return TranslationResult(
                    text="",
                    success=False,
                    error="Authentication required"
                )

            logger.info(f"User {user_id} requesting AI translation")

            # Get team AI settings if team_id provided
            ai_provider = None
            ai_model = None
            team_internal_id = None
            if input.team_id:
                ai_provider, ai_model = await get_team_ai_settings(input.team_id)
                # Get team internal id for token tracking
                async with AsyncSessionLocal() as db:
                    team = await TeamService.get_team_by_public_id(db, input.team_id)
                    if team:
                        team_internal_id = team.id

            # Perform translation
            translated_text, reason, used_provider, used_model, token_usage = await ai_service.translate(
                text=input.text,
                target_language=input.target_language,
                source_language=input.source_language,
                context=input.context,
                provider=ai_provider,
                model=ai_model,
            )

            # Record token usage if team_id provided
            if team_internal_id and token_usage.get("total_tokens", 0) > 0:
                async with AsyncSessionLocal() as db:
                    await TokenUsageService.record_usage(
                        db=db,
                        team_id=team_internal_id,
                        user_id=user_id,
                        operation_type="TRANSLATE",
                        provider=used_provider,
                        model=used_model,
                        input_tokens=token_usage.get("input_tokens", 0),
                        output_tokens=token_usage.get("output_tokens", 0),
            )

            if reason:
                # AI couldn't process the text
                return TranslationResult(
                    text="",
                    success=False,
                    reason=reason
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
            user_id = await get_current_user_id(info)
            if not user_id:
                return TranslationResult(
                    text="",
                    success=False,
                    error="Authentication required"
                )

            logger.info(f"User {user_id} requesting AI rephrase")

            # Get team AI settings if team_id provided
            ai_provider = None
            ai_model = None
            team_internal_id = None
            if input.team_id:
                ai_provider, ai_model = await get_team_ai_settings(input.team_id)
                async with AsyncSessionLocal() as db:
                    team = await TeamService.get_team_by_public_id(db, input.team_id)
                    if team:
                        team_internal_id = team.id

            # Perform rephrase
            rephrased_text, reason, used_provider, used_model, token_usage = await ai_service.rephrase(
                text=input.text,
                language=input.language,
                context=input.context,
                provider=ai_provider,
                model=ai_model,
            )

            # Record token usage if team_id provided
            if team_internal_id and token_usage.get("total_tokens", 0) > 0:
                async with AsyncSessionLocal() as db:
                    await TokenUsageService.record_usage(
                        db=db,
                        team_id=team_internal_id,
                        user_id=user_id,
                        operation_type="REPHRASE",
                        provider=used_provider,
                        model=used_model,
                        input_tokens=token_usage.get("input_tokens", 0),
                        output_tokens=token_usage.get("output_tokens", 0),
            )

            if reason:
                # AI couldn't process the text
                return TranslationResult(
                    text="",
                    success=False,
                    reason=reason
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
            user_id = await get_current_user_id(info)
            if not user_id:
                return TranslationResult(
                    text="",
                    success=False,
                    error="Authentication required"
                )

            logger.info(f"User {user_id} requesting AI shorten")

            # Get team AI settings if team_id provided
            ai_provider = None
            ai_model = None
            team_internal_id = None
            if input.team_id:
                ai_provider, ai_model = await get_team_ai_settings(input.team_id)
                async with AsyncSessionLocal() as db:
                    team = await TeamService.get_team_by_public_id(db, input.team_id)
                    if team:
                        team_internal_id = team.id

            # Perform shorten
            shortened_text, reason, used_provider, used_model, token_usage = await ai_service.shorten(
                text=input.text,
                language=input.language,
                context=input.context,
                provider=ai_provider,
                model=ai_model,
            )

            # Record token usage if team_id provided
            if team_internal_id and token_usage.get("total_tokens", 0) > 0:
                async with AsyncSessionLocal() as db:
                    await TokenUsageService.record_usage(
                        db=db,
                        team_id=team_internal_id,
                        user_id=user_id,
                        operation_type="SHORTEN",
                        provider=used_provider,
                        model=used_model,
                        input_tokens=token_usage.get("input_tokens", 0),
                        output_tokens=token_usage.get("output_tokens", 0),
            )

            if reason:
                # AI couldn't process the text
                return TranslationResult(
                    text="",
                    success=False,
                    reason=reason
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
            user_id = await get_current_user_id(info)
            if not user_id:
                return VariantsResult(
                    variants=[],
                    success=False,
                    error="Authentication required"
                )

            logger.info(f"User {user_id} requesting AI variants")

            # Get team AI settings if team_id provided
            ai_provider = None
            ai_model = None
            team_internal_id = None
            if input.team_id:
                ai_provider, ai_model = await get_team_ai_settings(input.team_id)
                async with AsyncSessionLocal() as db:
                    team = await TeamService.get_team_by_public_id(db, input.team_id)
                    if team:
                        team_internal_id = team.id

            # Generate variants
            variants, reason, used_provider, used_model, token_usage = await ai_service.suggest_variants(
                text=input.text,
                language=input.language,
                context=input.context,
                count=input.count or 3,
                provider=ai_provider,
                model=ai_model,
            )

            # Record token usage if team_id provided
            if team_internal_id and token_usage.get("total_tokens", 0) > 0:
                async with AsyncSessionLocal() as db:
                    await TokenUsageService.record_usage(
                        db=db,
                        team_id=team_internal_id,
                        user_id=user_id,
                        operation_type="VARIANTS",
                        provider=used_provider,
                        model=used_model,
                        input_tokens=token_usage.get("input_tokens", 0),
                        output_tokens=token_usage.get("output_tokens", 0),
            )

            if reason:
                # AI couldn't process the text
                return VariantsResult(
                    variants=[],
                    success=False,
                    reason=reason
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

