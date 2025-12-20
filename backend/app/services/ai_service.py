"""
AI Service for translation assistance using OpenAI and Anthropic APIs
"""
from typing import Optional
import logging
import json
import httpx
from openai import AsyncOpenAI, OpenAIError
from app.core.config import settings

logger = logging.getLogger(__name__)


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
    ) -> str:
        """Call Anthropic API and return response text."""
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
            content = data.get("content", [])
            if not content:
                raise Exception("Empty response from Anthropic")
            
            return content[0].get("text", "").strip()
    
    async def _call_openai(
        self,
        system_content: str,
        user_content: str,
        model: str,
        temperature: float = 1.0,
        json_mode: bool = True,
    ) -> str:
        """Call OpenAI API and return response text."""
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ],
            max_tokens=settings.openai_max_tokens,
            temperature=temperature,
            response_format={"type": "json_object"} if json_mode else None,
        )
        return response.choices[0].message.content.strip()
    
    async def _call_ai(
        self,
        system_content: str,
        user_content: str,
        provider: str,
        model: str,
        temperature: float = 1.0,
    ) -> str:
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
    ) -> tuple[str, Optional[str]]:
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
            Tuple of (translated_text, reason_if_failed)
            - If successful: (translation, None)
            - If failed: ("", reason)
            
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
            
            response_text = await self._call_ai(
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
                return ("", reason)
            
            translation = response_data.get("result", "").strip()
            if not translation:
                return ("", "Translation result is empty")
            
            logger.info("Translation completed successfully")
            return (translation, None)

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
    ) -> tuple[str, Optional[str]]:
        """
        Rephrase text while maintaining meaning
        
        Args:
            text: Text to rephrase
            language: Language of the text
            context: Optional context
            provider: AI provider to use (OPENAI or ANTHROPIC)
            model: Specific model to use
            
        Returns:
            Tuple of (rephrased_text, reason_if_failed)
            - If successful: (rephrased, None)
            - If failed: ("", reason)
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
            
            response_text = await self._call_ai(
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
                return ("", reason)
            
            rephrased = response_data.get("result", "").strip()
            if not rephrased:
                return ("", "Rephrase result is empty")
            
            logger.info("Rephrase completed successfully")
            return (rephrased, None)

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
    ) -> tuple[str, Optional[str]]:
        """
        Shorten text while preserving key meaning
        
        Args:
            text: Text to shorten
            language: Language of the text
            context: Optional context
            provider: AI provider to use (OPENAI or ANTHROPIC)
            model: Specific model to use
            
        Returns:
            Tuple of (shortened_text, reason_if_failed)
            - If successful: (shortened, None)
            - If failed: ("", reason)
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
            
            response_text = await self._call_ai(
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
                return ("", reason)
            
            shortened = response_data.get("result", "").strip()
            if not shortened:
                return ("", "Shorten result is empty")
            
            logger.info("Shorten completed successfully")
            return (shortened, None)

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
    ) -> tuple[list[str], Optional[str]]:
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
            Tuple of (variants_list, reason_if_failed)
            - If successful: ([variants], None)
            - If failed: ([], reason)
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
            
            response_text = await self._call_ai(
                system_content=system_content,
                user_content=user_content,
                provider=use_provider,
                model=use_model,
                temperature=1.2,  # Higher temperature for more variety
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
                return ([], reason)
            
            variants = response_data.get("variants", [])
            if not variants or len(variants) == 0:
                return ([], "No variants generated")
            
            logger.info(f"Generated {len(variants)} variants successfully")
            return (variants[:count], None)  # Ensure we don't return more than requested

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception("Variant generation failed. Please try again.")
        except Exception as e:
            logger.error(f"Variant generation error: {type(e).__name__}: {str(e)}")
            raise Exception("Variant generation failed. Please try again.")


# Global instance
ai_service = AIService()

