"""
AI Service for translation assistance using OpenAI and Anthropic APIs
"""
from typing import Optional, TypedDict
import logging
import json
import httpx
from openai import AsyncOpenAI, OpenAIError
from app.core.config import settings

logger = logging.getLogger(__name__)


# Type definitions for code analysis
class TokenUsageInfo(TypedDict):
    """Type definition for token usage information."""
    input_tokens: int
    output_tokens: int
    total_tokens: int


class FoundStringInfo(TypedDict):
    """Type definition for a found string in code."""
    text: str
    line: int
    suggested_key: str
    context: str
    confidence: float


class AnalysisResult(TypedDict):
    """Type definition for file analysis result."""
    strings: list[FoundStringInfo]
    token_usage: TokenUsageInfo


# Available models for each provider
AVAILABLE_MODELS = {
    "OPENAI": [
        {"id": "gpt-5.2-2025-12-11", "name": "GPT-5.2", "description": "Best for coding and agentic tasks"},
        {"id": "gpt-5-mini-2025-08-07", "name": "GPT-5 Mini", "description": "Faster, cost-efficient for well-defined tasks"},
        {"id": "gpt-5-nano-2025-08-07", "name": "GPT-5 Nano", "description": "Fastest, most cost-efficient"},
    ],
    "ANTHROPIC": [
        {"id": "claude-opus-4-5", "name": "Claude Opus 4.5", "description": "Premium model with maximum intelligence"},
        {"id": "claude-sonnet-4-5", "name": "Claude Sonnet 4.5", "description": "Smart model for complex agents and coding"},
        {"id": "claude-haiku-4-5", "name": "Claude Haiku 4.5", "description": "Fastest with near-frontier intelligence"},
    ],
}


def get_available_models():
    """Return available models for all providers."""
    return AVAILABLE_MODELS


class AIService:
    """Service for AI-powered translation operations"""
    
    ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

    def __init__(self):
        """Initialize API clients"""
        # OpenAI client
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured")
            self.openai_client = None
        else:
            self.openai_client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                timeout=settings.openai_timeout
            )
        
        # Anthropic API key
        if not settings.anthropic_api_key:
            logger.warning("Anthropic API key not configured")
            self.anthropic_api_key = None
        else:
            self.anthropic_api_key = settings.anthropic_api_key

    def _is_available(self, provider: Optional[str] = None) -> bool:
        """Check if AI service is available for given provider"""
        if provider == "ANTHROPIC":
            return self.anthropic_api_key is not None
        # Default to OpenAI
        return self.openai_client is not None
    
    def _get_default_model(self, provider: str) -> str:
        """Get default model for a provider"""
        if provider == "ANTHROPIC":
            return settings.anthropic_model
        return settings.openai_text_model
    
    async def _call_anthropic(
        self,
        system_content: str,
        user_content: str,
        model: str,
    ) -> tuple[str, TokenUsageInfo]:
        """Call Anthropic API and return response text with token usage."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.ANTHROPIC_API_URL,
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": settings.openai_max_tokens,
                    "system": system_content,
                    "messages": [{"role": "user", "content": user_content}],
                },
                timeout=settings.openai_timeout,
            )
            
            if response.status_code != 200:
                logger.error(f"Anthropic API error: {response.status_code} - {response.text}")
                raise Exception("AI request failed")
            
            data = response.json()
            usage = data.get("usage", {})
            token_usage: TokenUsageInfo = {
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            }
            content = data.get("content", [])
            if not content:
                raise Exception("Empty response from Anthropic")
            
            return content[0].get("text", "").strip(), token_usage
    
    async def _call_openai(
        self,
        system_content: str,
        user_content: str,
        model: str,
        temperature: float = 1.0,
        json_mode: bool = True,
    ) -> tuple[str, TokenUsageInfo]:
        """Call OpenAI API and return response text with token usage."""
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ],
            max_completion_tokens=settings.openai_max_tokens,
            temperature=temperature,
            response_format={"type": "json_object"} if json_mode else None,
        )
        usage = response.usage
        token_usage: TokenUsageInfo = {
            "input_tokens": usage.prompt_tokens if usage else 0,
            "output_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
        }
        return response.choices[0].message.content.strip(), token_usage
    
    async def _call_ai(
        self,
        system_content: str,
        user_content: str,
        provider: str,
        model: str,
        temperature: float = 1.0,
    ) -> tuple[str, TokenUsageInfo]:
        """Universal AI call method that handles both providers."""
        if provider == "ANTHROPIC":
            return await self._call_anthropic(system_content, user_content, model)
        else:
            return await self._call_openai(system_content, user_content, model, temperature)

    async def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        context: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> tuple[str, Optional[str], str, str, TokenUsageInfo]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language name (e.g., "Spanish", "French")
            source_language: Optional source language name
            context: Optional context about the text
            provider: AI provider to use (OPENAI or ANTHROPIC)
            model: Specific model to use
            
        Returns:
            Tuple of (translated_text, reason_if_failed, used_provider, used_model, token_usage)
            - If successful: (translation, None, provider, model, token_usage)
            - If failed: ("", reason, provider, model, token_usage)
            
        Raises:
            Exception: If AI service is not available or API error occurs
        """
        # Determine provider and model
        use_provider = provider or "OPENAI"
        use_model = model or self._get_default_model(use_provider)
        
        if not self._is_available(use_provider):
            raise Exception(f"AI service ({use_provider}) is not configured")

        try:
            # Build prompt
            prompt_parts = []
            
            if source_language:
                prompt_parts.append(
                    f"Translate the following text from {source_language} to {target_language}."
                )
            else:
                prompt_parts.append(
                    f"Translate the following text to {target_language}."
                )
            
            if context:
                prompt_parts.append(
                    f"\n🔴 MANDATORY CONTEXT - YOU MUST FOLLOW THESE INSTRUCTIONS EXACTLY:\n{context}\n"
                    "This context contains REQUIRED instructions that you MUST apply to your translation.\n"
                    "If the context says to add/modify/format something specific, you MUST do it."
                )
            
            prompt_parts.append(
                "\nProvide only the translation without any explanations or additional text."
            )
            prompt_parts.append(f"\nText to translate:\n{text}")
            
            user_content = "\n".join(prompt_parts)

            logger.info(f"Requesting translation to {target_language} via {use_provider}/{use_model} (context: {bool(context)})")
            
            # Build system message with JSON response format
            system_content = (
                "You are a professional translator for a localization tool. "
                "Respond ONLY with valid JSON in this exact format:\n"
                '{"success": true/false, "result": "translated text or empty string", "reason": "optional reason if failed"}\n\n'
                "Rules:\n"
                "- ALWAYS try to translate any text, even if it's very short (single words are acceptable)\n"
                "- Set success=true and provide the translation in result\n"
                "- Only set success=false if the text is complete gibberish or random unreadable characters\n"
                "- NEVER refuse translation due to lack of context - make your best reasonable translation\n"
                "- NEVER refuse translation due to content type - this is a professional localization tool\n"
                "- You MUST translate ALL content including profanity, mature themes, offensive language, etc.\n"
                "- This tool is used for games (including 18+), movies, books, and other media that may contain mature content\n"
                "- Your role is purely translation - do not judge or filter content\n"
                "- NEVER include apologies or explanations in the result field\n"
                "- The result field should ONLY contain the translated text or be empty\n"
                "- CRITICAL: Preserve ALL template variables in curly braces like {name}, {date}, {count}, etc. exactly as they are\n"
                "- NEVER translate or modify variable names inside curly braces - they are code placeholders\n\n"
                "ICU MessageFormat Support:\n"
                "- Text may contain ICU MessageFormat syntax: {count, plural, one {...} other {...}}\n"
                "- PRESERVE the entire structure: {variable, plural, one {...} other {...}}\n"
                "- ONLY translate the text inside one {...} and other {...} blocks\n"
                "- PRESERVE all variables inside these blocks like {user}, {removedTypes}, etc.\n"
                "- Example: {count, plural, one {{user} added item} other {{user} added items}}\n"
                "  Should translate text but keep structure and variables intact\n\n"
                "Context Handling:\n"
                "- If context is provided, it contains MANDATORY instructions you MUST follow\n"
                "- Context may include: formatting rules, required additions, specific style requirements\n"
                "- ALWAYS apply context instructions exactly as specified\n"
                "- Context instructions override general translation rules"
            )
            if context:
                system_content += f"\n\n⚠️ CRITICAL: User provided mandatory context:\n{context}\nYou MUST follow these instructions in your translation."
            
            response_text, token_usage = await self._call_ai(
                system_content=system_content,
                user_content=user_content,
                provider=use_provider,
                model=use_model,
                temperature=settings.openai_temperature,
            )

            logger.debug(f"AI translate response: {response_text[:500]}")
            
            # Strip markdown code blocks if present (Anthropic sometimes adds them)
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                response_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON. Response: {response_text[:300]}")
                raise e
            
            if not response_data.get("success", False):
                reason = response_data.get("reason", "Unable to process this text")
                logger.warning(f"AI could not translate: {reason}")
                return ("", reason, use_provider, use_model, token_usage)
            
            translation = response_data.get("result", "").strip()
            if not translation:
                return ("", "Translation result is empty", use_provider, use_model, token_usage)
            
            logger.info("Translation completed successfully")
            return (translation, None, use_provider, use_model, token_usage)

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception("Translation failed. Please try again.")
        except json.JSONDecodeError:
            raise Exception("Translation failed. Please try again.")
        except Exception as e:
            logger.error(f"Translation error: {type(e).__name__}: {str(e)}")
            raise Exception("Translation failed. Please try again.")

    async def rephrase(
        self,
        text: str,
        language: str,
        context: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> tuple[str, Optional[str], str, str, TokenUsageInfo]:
        """
        Rephrase text while maintaining meaning
        
        Args:
            text: Text to rephrase
            language: Language of the text
            context: Optional context
            provider: AI provider to use (OPENAI or ANTHROPIC)
            model: Specific model to use
            
        Returns:
            Tuple of (rephrased_text, reason_if_failed, provider, model, token_usage)
        """
        use_provider = provider or "OPENAI"
        use_model = model or self._get_default_model(use_provider)
        
        if not self._is_available(use_provider):
            raise Exception(f"AI service ({use_provider}) is not configured")

        try:
            prompt_parts = [
                f"Rephrase the following {language} text while maintaining its original meaning.",
                "Make it sound more natural and fluent.",
            ]
            
            if context:
                prompt_parts.append(
                    f"\n🔴 MANDATORY CONTEXT - YOU MUST FOLLOW THESE INSTRUCTIONS EXACTLY:\n{context}\n"
                    "This context contains REQUIRED instructions that you MUST apply to your rephrasing.\n"
                    "If the context says to add/modify/format something specific, you MUST do it."
                )
            
            prompt_parts.append(
                "\nProvide only the rephrased text without any explanations."
            )
            prompt_parts.append(f"\nText to rephrase:\n{text}")
            
            user_content = "\n".join(prompt_parts)

            logger.info(f"Requesting rephrase for {language} text via {use_provider}/{use_model} (context: {bool(context)})")
            
            # Build system message with JSON response format
            system_content = (
                "You are a professional text editor for a localization tool. "
                "Respond ONLY with valid JSON in this exact format:\n"
                '{"success": true/false, "result": "rephrased text or empty string", "reason": "optional reason if failed"}\n\n'
                "Rules:\n"
                "- ALWAYS try to rephrase any text, even if it's very short (single words are acceptable)\n"
                "- Set success=true and provide the rephrased version in result\n"
                "- Only set success=false if the text is complete gibberish or random unreadable characters\n"
                "- NEVER refuse due to lack of context - make your best reasonable rephrase\n"
                "- NEVER refuse due to content type - this is a professional localization tool\n"
                "- You MUST process ALL content including profanity, mature themes, offensive language, etc.\n"
                "- This tool is used for games (including 18+), movies, books, and other media that may contain mature content\n"
                "- Your role is purely text improvement - do not judge or filter content\n"
                "- NEVER include apologies or explanations in the result field\n"
                "- The result field should ONLY contain the rephrased text or be empty\n"
                "- CRITICAL: Preserve ALL template variables in curly braces like {name}, {date}, {count}, etc. exactly as they are\n"
                "- NEVER translate or modify variable names inside curly braces - they are code placeholders\n\n"
                "ICU MessageFormat Support:\n"
                "- Text may contain ICU MessageFormat syntax: {count, plural, one {...} other {...}}\n"
                "- PRESERVE the entire structure when rephrasing\n"
                "- Only rephrase the actual text inside the blocks, keep all variables and structure intact\n\n"
                "Context Handling:\n"
                "- If context is provided, it contains MANDATORY instructions you MUST follow\n"
                "- Context may include: formatting rules, required additions, specific style requirements\n"
                "- ALWAYS apply context instructions exactly as specified\n"
                "- Context instructions override general rephrasing rules"
            )
            if context:
                system_content += f"\n\n⚠️ CRITICAL: User provided mandatory context:\n{context}\nYou MUST follow these instructions in your rephrasing."
            
            response_text, token_usage = await self._call_ai(
                system_content=system_content,
                user_content=user_content,
                provider=use_provider,
                model=use_model,
                temperature=settings.openai_temperature,
            )

            # Strip markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            response_data = json.loads(response_text)
            
            if not response_data.get("success", False):
                reason = response_data.get("reason", "Unable to process this text")
                logger.warning(f"AI could not rephrase: {reason}")
                return ("", reason, use_provider, use_model, token_usage)
            
            rephrased = response_data.get("result", "").strip()
            if not rephrased:
                return ("", "Rephrase result is empty", use_provider, use_model, token_usage)
            
            logger.info("Rephrase completed successfully")
            return (rephrased, None, use_provider, use_model, token_usage)

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception("Rephrase failed. Please try again.")
        except Exception as e:
            logger.error(f"Rephrase error: {type(e).__name__}: {str(e)}")
            raise Exception("Rephrase failed. Please try again.")

    async def shorten(
        self,
        text: str,
        language: str,
        context: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> tuple[str, Optional[str], str, str, TokenUsageInfo]:
        """
        Shorten text while preserving key meaning
        
        Args:
            text: Text to shorten
            language: Language of the text
            context: Optional context
            provider: AI provider to use (OPENAI or ANTHROPIC)
            model: Specific model to use
            
        Returns:
            Tuple of (shortened_text, reason_if_failed, provider, model, token_usage)
        """
        use_provider = provider or "OPENAI"
        use_model = model or self._get_default_model(use_provider)
        
        if not self._is_available(use_provider):
            raise Exception(f"AI service ({use_provider}) is not configured")

        try:
            prompt_parts = [
                f"Shorten the following {language} text while preserving its key meaning.",
                "Make it concise and clear.",
            ]
            
            if context:
                prompt_parts.append(
                    f"\n🔴 MANDATORY CONTEXT - YOU MUST FOLLOW THESE INSTRUCTIONS EXACTLY:\n{context}\n"
                    "This context contains REQUIRED instructions that you MUST apply to your shortened version.\n"
                    "If the context says to add/modify/format something specific, you MUST do it."
                )
            
            prompt_parts.append(
                "\nProvide only the shortened text without any explanations."
            )
            prompt_parts.append(f"\nText to shorten:\n{text}")
            
            user_content = "\n".join(prompt_parts)

            logger.info(f"Requesting shorten for {language} text via {use_provider}/{use_model} (context: {bool(context)})")
            
            # Build system message with JSON response format
            system_content = (
                "You are a professional text editor for a localization tool. "
                "Respond ONLY with valid JSON in this exact format:\n"
                '{"success": true/false, "result": "shortened text or empty string", "reason": "optional reason if failed"}\n\n'
                "Rules:\n"
                "- ALWAYS try to shorten any text, even if it's already short\n"
                "- Set success=true and provide the shortened version in result\n"
                "- Only set success=false if the text is complete gibberish or random unreadable characters\n"
                "- If text is already very short, provide a more concise alternative\n"
                "- NEVER refuse due to lack of context - make your best reasonable shortening\n"
                "- NEVER refuse due to content type - this is a professional localization tool\n"
                "- You MUST process ALL content including profanity, mature themes, offensive language, etc.\n"
                "- This tool is used for games (including 18+), movies, books, and other media that may contain mature content\n"
                "- Your role is purely text improvement - do not judge or filter content\n"
                "- NEVER include apologies or explanations in the result field\n"
                "- The result field should ONLY contain the shortened text or be empty\n"
                "- CRITICAL: Preserve ALL template variables in curly braces like {name}, {date}, {count}, etc. exactly as they are\n"
                "- NEVER translate or modify variable names inside curly braces - they are code placeholders\n\n"
                "ICU MessageFormat Support:\n"
                "- Text may contain ICU MessageFormat syntax: {count, plural, one {...} other {...}}\n"
                "- PRESERVE the entire structure when shortening\n"
                "- Only shorten the actual text inside the blocks, keep all variables and structure intact\n\n"
                "Context Handling:\n"
                "- If context is provided, it contains MANDATORY instructions you MUST follow\n"
                "- Context may include: formatting rules, required additions, specific style requirements\n"
                "- ALWAYS apply context instructions exactly as specified\n"
                "- Context instructions override general shortening rules"
            )
            if context:
                system_content += f"\n\n⚠️ CRITICAL: User provided mandatory context:\n{context}\nYou MUST follow these instructions in your shortened version."
            
            response_text, token_usage = await self._call_ai(
                system_content=system_content,
                user_content=user_content,
                provider=use_provider,
                model=use_model,
                temperature=settings.openai_temperature,
            )

            # Strip markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            response_data = json.loads(response_text)
            
            if not response_data.get("success", False):
                reason = response_data.get("reason", "Unable to process this text")
                logger.warning(f"AI could not shorten: {reason}")
                return ("", reason, use_provider, use_model, token_usage)
            
            shortened = response_data.get("result", "").strip()
            if not shortened:
                return ("", "Shorten result is empty", use_provider, use_model, token_usage)
            
            logger.info("Shorten completed successfully")
            return (shortened, None, use_provider, use_model, token_usage)

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception("Shorten failed. Please try again.")
        except Exception as e:
            logger.error(f"Shorten error: {type(e).__name__}: {str(e)}")
            raise Exception("Shorten failed. Please try again.")

    async def suggest_variants(
        self,
        text: str,
        language: str,
        context: Optional[str] = None,
        count: int = 3,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> tuple[list[str], Optional[str], str, str, TokenUsageInfo]:
        """
        Generate alternative variants of the text
        
        Args:
            text: Text to generate variants for
            language: Language of the text
            context: Optional context
            count: Number of variants to generate (default: 3)
            provider: AI provider to use (OPENAI or ANTHROPIC)
            model: Specific model to use
            
        Returns:
            Tuple of (variants_list, reason_if_failed, provider, model, token_usage)
        """
        use_provider = provider or "OPENAI"
        use_model = model or self._get_default_model(use_provider)
        
        if not self._is_available(use_provider):
            raise Exception(f"AI service ({use_provider}) is not configured")

        try:
            prompt_parts = [
                f"Generate {count} alternative variants of the following {language} text.",
                "Each variant should have a slightly different tone or wording while maintaining the same meaning.",
            ]
            
            if context:
                prompt_parts.append(
                    f"\n🔴 MANDATORY CONTEXT - YOU MUST FOLLOW THESE INSTRUCTIONS EXACTLY:\n{context}\n"
                    "This context contains REQUIRED instructions that you MUST apply to ALL variants.\n"
                    "If the context says to add/modify/format something specific, you MUST do it in EVERY variant."
                )
            
            prompt_parts.append(
                f"\nProvide exactly {count} variants, each on a new line, numbered 1., 2., 3., etc."
            )
            prompt_parts.append(f"\nText:\n{text}")
            
            user_content = "\n".join(prompt_parts)

            logger.info(f"Requesting {count} variants for {language} text via {use_provider}/{use_model} (context: {bool(context)})")
            
            # Build system message with JSON response format
            system_content = (
                "You are a creative text editor for a localization tool. "
                "Respond ONLY with valid JSON in this exact format:\n"
                '{"success": true/false, "variants": ["variant1", "variant2", "variant3"], "reason": "optional reason if failed"}\n\n'
                "Rules:\n"
                f"- ALWAYS try to generate variants for any text, even if it's very short (single words are acceptable)\n"
                f"- Set success=true and provide exactly {count} variants in the variants array\n"
                "- Only set success=false if the text is complete gibberish or random unreadable characters\n"
                "- NEVER refuse due to lack of context - make your best reasonable variants\n"
                "- NEVER refuse due to content type - this is a professional localization tool\n"
                "- You MUST process ALL content including profanity, mature themes, offensive language, etc.\n"
                "- This tool is used for games (including 18+), movies, books, and other media that may contain mature content\n"
                "- Your role is purely text improvement - do not judge or filter content\n"
                "- NEVER include apologies or explanations in the variants\n"
                "- Each variant should be a natural alternative with different wording\n"
                "- CRITICAL: Preserve ALL template variables in curly braces like {name}, {date}, {count}, etc. exactly as they are\n"
                "- NEVER translate or modify variable names inside curly braces - they are code placeholders\n\n"
                "ICU MessageFormat Support:\n"
                "- Text may contain ICU MessageFormat syntax: {count, plural, one {...} other {...}}\n"
                "- PRESERVE the entire structure in all variants\n"
                "- Only vary the actual text inside the blocks, keep all variables and structure intact\n\n"
                "Context Handling:\n"
                "- If context is provided, it contains MANDATORY instructions you MUST follow\n"
                "- Context may include: formatting rules, required additions, specific style requirements\n"
                "- ALWAYS apply context instructions exactly as specified in ALL variants\n"
                "- Context instructions override general variant generation rules"
            )
            if context:
                system_content += f"\n\n⚠️ CRITICAL: User provided mandatory context:\n{context}\nYou MUST follow these instructions in ALL variants you generate."
            
            response_text, token_usage = await self._call_ai(
                system_content=system_content,
                user_content=user_content,
                provider=use_provider,
                model=use_model,
                temperature=1.0,  # GPT-5 models only support temperature=1
            )

            # Strip markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            response_data = json.loads(response_text)
            
            if not response_data.get("success", False):
                reason = response_data.get("reason", "Unable to process this text")
                logger.warning(f"AI could not generate variants: {reason}")
                return ([], reason, use_provider, use_model, token_usage)
            
            variants = response_data.get("variants", [])
            if not variants or len(variants) == 0:
                return ([], "No variants generated", use_provider, use_model, token_usage)
            
            logger.info(f"Generated {len(variants)} variants successfully")
            return (variants[:count], None, use_provider, use_model, token_usage)

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception("Variant generation failed. Please try again.")
        except Exception as e:
            logger.error(f"Variant generation error: {type(e).__name__}: {str(e)}")
            raise Exception("Variant generation failed. Please try again.")

    async def analyze_file_for_strings(
        self,
        file_content: str,
        file_path: str,
        i18n_framework: Optional[str] = None,
        existing_keys: Optional[list[str]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AnalysisResult:
        """
        Analyze a source file to find hardcoded strings that need localization.
        
        Args:
            file_content: Content of the source file
            file_path: Path to the file (for context)
            i18n_framework: Optional i18n framework name (react-i18next, vue-i18n, etc.)
            existing_keys: Optional list of existing translation keys to avoid duplicates
            provider: AI provider to use (OPENAI or ANTHROPIC)
            model: Specific model to use
            
        Returns:
            AnalysisResult with found strings and token usage
        """
        use_provider = provider or "OPENAI"
        use_model = model or self._get_default_model(use_provider)
        
        if not self._is_available(use_provider):
            raise Exception(f"AI service ({use_provider}) is not configured")
        
        # Build the system prompt
        system_prompt = self._build_analysis_system_prompt(i18n_framework, existing_keys)
        
        # Build the user prompt
        user_prompt = self._build_analysis_user_prompt(file_content, file_path)
        
        try:
            if use_provider == "ANTHROPIC":
                return await self._analyze_with_anthropic(system_prompt, user_prompt, use_model)
            else:
                return await self._analyze_with_openai(system_prompt, user_prompt, use_model)
        except Exception as e:
            logger.error(f"Analysis error ({use_provider}): {type(e).__name__}: {str(e)}")
            raise Exception("Failed to analyze file. Please try again.")

    async def _analyze_with_anthropic(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
    ) -> AnalysisResult:
        """Call Anthropic API for file analysis."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.ANTHROPIC_API_URL,
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 4096,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
                timeout=120.0,
            )
            
            if response.status_code != 200:
                logger.error(f"Anthropic API error: {response.status_code} - {response.text}")
                raise Exception("AI request failed")
            
            data = response.json()
            
            # Extract token usage
            usage = data.get("usage", {})
            token_usage: TokenUsageInfo = {
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            }
            
            # Extract content
            content = data.get("content", [])
            if not content:
                return {"strings": [], "token_usage": token_usage}
            
            response_text = content[0].get("text", "")
            return self._parse_analysis_response(response_text, token_usage)

    async def _analyze_with_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
    ) -> AnalysisResult:
        """Call OpenAI API for file analysis."""
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=4096,
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Extract token usage
        usage = response.usage
        token_usage: TokenUsageInfo = {
            "input_tokens": usage.prompt_tokens if usage else 0,
            "output_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
        }
        
        return self._parse_analysis_response(response_text, token_usage)

    def _parse_analysis_response(
        self,
        response_text: str,
        token_usage: TokenUsageInfo,
    ) -> AnalysisResult:
        """Parse the AI response and extract found strings."""
        # Strip markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        try:
            result = json.loads(response_text)
            
            # Handle both formats: {"strings": [...]} and direct array [...]
            if isinstance(result, list):
                strings = result
            elif isinstance(result, dict):
                strings = result.get("strings", [])
            else:
                strings = []
            
            # Validate and normalize strings
            validated_strings: list[FoundStringInfo] = []
            for s in strings:
                if isinstance(s, dict) and "text" in s and "suggested_key" in s:
                    validated_strings.append({
                        "text": str(s.get("text", "")),
                        "line": int(s.get("line", 0)),
                        "suggested_key": str(s.get("suggested_key", "")),
                        "context": str(s.get("context", "")),
                        "confidence": float(s.get("confidence", 0.8)),
                    })
            
            return {"strings": validated_strings, "token_usage": token_usage}
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response: {response_text[:500]}")
            return {"strings": [], "token_usage": token_usage}

    def _build_analysis_system_prompt(
        self,
        i18n_framework: Optional[str] = None,
        existing_keys: Optional[list[str]] = None,
    ) -> str:
        """Build the system prompt for file analysis."""
        framework_context = ""
        if i18n_framework:
            framework_context = f"""
The project uses {i18n_framework} for internationalization.
When generating keys, follow the conventions typical for {i18n_framework}.
"""
        
        existing_keys_context = ""
        if existing_keys:
            keys_sample = existing_keys[:50]  # Limit to avoid huge prompts
            existing_keys_context = f"""
Existing translation keys in the project (sample):
{', '.join(keys_sample)}

Try to follow the existing naming conventions and avoid duplicating these keys.
"""
        
        return f"""You are an expert code analyzer specializing in internationalization (i18n).
Your task is to analyze source code files and identify user-facing strings that should be localized.

{framework_context}
{existing_keys_context}

RULES FOR IDENTIFYING STRINGS TO LOCALIZE:
1. INCLUDE (should be localized):
   - UI text: button labels, headings, descriptions, placeholders
   - Error messages shown to users
   - Tooltips and help text
   - Form labels and validation messages
   - Navigation items and menu text
   - Notification and toast messages

2. EXCLUDE (do NOT localize):
   - Technical strings: URLs, API endpoints, file paths
   - CSS class names and IDs
   - Console.log messages and debug output
   - Variable names and code identifiers
   - Strings already wrapped in i18n functions (t(), $t(), etc.)
   - HTML attributes like "type", "name", "id"
   - Empty strings or whitespace-only strings
   - Single characters or punctuation

KEY NAMING CONVENTIONS:
- Use dot notation: namespace.component.element
- Keep keys descriptive but concise
- Use lowercase with camelCase for multi-word parts
- Examples:
  - auth.login.title -> "Welcome Back"
  - auth.login.submitButton -> "Sign In"
  - common.buttons.save -> "Save"
  - errors.validation.required -> "This field is required"

RESPONSE FORMAT:
You MUST respond with valid JSON only, no other text. Use this exact format:
{{
  "strings": [
    {{
      "text": "The exact string found in code",
      "line": 24,
      "suggested_key": "namespace.component.element",
      "context": "Brief description of where/how this string is used",
      "confidence": 0.95
    }}
  ]
}}

If no strings need localization, return: {{"strings": []}}
"""

    def _build_analysis_user_prompt(self, file_content: str, file_path: str) -> str:
        """Build the user prompt for file analysis."""
        # Determine file type from path
        file_type = "unknown"
        if file_path.endswith((".tsx", ".jsx")):
            file_type = "React component"
        elif file_path.endswith(".vue"):
            file_type = "Vue component"
        elif file_path.endswith(".svelte"):
            file_type = "Svelte component"
        elif file_path.endswith((".ts", ".js")):
            file_type = "JavaScript/TypeScript"
        elif file_path.endswith(".py"):
            file_type = "Python"
        
        return f"""Analyze this {file_type} file and find all user-facing strings that need localization.

File path: {file_path}

```
{file_content}
```

Remember: Return ONLY valid JSON with the found strings. Do not include any explanations or markdown formatting."""


# Global instance
ai_service = AIService()

