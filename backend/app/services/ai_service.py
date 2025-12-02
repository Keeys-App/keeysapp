"""
AI Service for translation assistance using OpenAI API
"""
from typing import Optional
import logging
import json
from openai import AsyncOpenAI, OpenAIError
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered translation operations"""

    def __init__(self):
        """Initialize OpenAI client"""
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured")
            self.client = None
        else:
            self.client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                timeout=settings.openai_timeout
            )

    def _is_available(self) -> bool:
        """Check if AI service is available"""
        return self.client is not None

    async def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        context: Optional[str] = None
    ) -> tuple[str, Optional[str]]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language name (e.g., "Spanish", "French")
            source_language: Optional source language name
            context: Optional context about the text
            
        Returns:
            Tuple of (translated_text, reason_if_failed)
            - If successful: (translation, None)
            - If failed: ("", reason)
            
        Raises:
            Exception: If AI service is not available or API error occurs
        """
        if not self._is_available():
            raise Exception("AI service is not configured")

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
            
            prompt = "\n".join(prompt_parts)

            logger.info(f"Requesting translation to {target_language} (context: {bool(context)})")
            
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
            
            response = await self.client.chat.completions.create(
                model=settings.openai_text_model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.openai_max_tokens,
                temperature=settings.openai_temperature,
                response_format={"type": "json_object"}
            )

            # Parse JSON response
            response_text = response.choices[0].message.content.strip()
            logger.debug(f"AI translate response: {response_text[:500]}")
            
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
        context: Optional[str] = None
    ) -> tuple[str, Optional[str]]:
        """
        Rephrase text while maintaining meaning
        
        Args:
            text: Text to rephrase
            language: Language of the text
            context: Optional context
            
        Returns:
            Tuple of (rephrased_text, reason_if_failed)
            - If successful: (rephrased, None)
            - If failed: ("", reason)
        """
        if not self._is_available():
            raise Exception("AI service is not configured")

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
            
            prompt = "\n".join(prompt_parts)

            logger.info(f"Requesting rephrase for {language} text (context: {bool(context)})")
            
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
            
            response = await self.client.chat.completions.create(
                model=settings.openai_text_model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.openai_max_tokens,
                temperature=settings.openai_temperature,
                response_format={"type": "json_object"}
            )

            # Parse JSON response
            response_text = response.choices[0].message.content.strip()
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
        context: Optional[str] = None
    ) -> tuple[str, Optional[str]]:
        """
        Shorten text while preserving key meaning
        
        Args:
            text: Text to shorten
            language: Language of the text
            context: Optional context
            
        Returns:
            Tuple of (shortened_text, reason_if_failed)
            - If successful: (shortened, None)
            - If failed: ("", reason)
        """
        if not self._is_available():
            raise Exception("AI service is not configured")

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
            
            prompt = "\n".join(prompt_parts)

            logger.info(f"Requesting shorten for {language} text (context: {bool(context)})")
            
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
            
            response = await self.client.chat.completions.create(
                model=settings.openai_text_model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.openai_max_tokens,
                temperature=settings.openai_temperature,
                response_format={"type": "json_object"}
            )

            # Parse JSON response
            response_text = response.choices[0].message.content.strip()
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
        count: int = 3
    ) -> tuple[list[str], Optional[str]]:
        """
        Generate alternative variants of the text
        
        Args:
            text: Text to generate variants for
            language: Language of the text
            context: Optional context
            count: Number of variants to generate (default: 3)
            
        Returns:
            Tuple of (variants_list, reason_if_failed)
            - If successful: ([variants], None)
            - If failed: ([], reason)
        """
        if not self._is_available():
            raise Exception("AI service is not configured")

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
            
            prompt = "\n".join(prompt_parts)

            logger.info(f"Requesting {count} variants for {language} text (context: {bool(context)})")
            
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
            
            response = await self.client.chat.completions.create(
                model=settings.openai_text_model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.openai_max_tokens,
                temperature=1.2,  # Higher temperature for more variety
                response_format={"type": "json_object"}
            )

            # Parse JSON response
            response_text = response.choices[0].message.content.strip()
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

