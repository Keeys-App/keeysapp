"""
AI Service for translation assistance using OpenAI API
"""
from typing import Optional
import logging
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
    ) -> str:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language name (e.g., "Spanish", "French")
            source_language: Optional source language name
            context: Optional context about the text
            
        Returns:
            Translated text
            
        Raises:
            Exception: If AI service is not available or translation fails
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
                prompt_parts.append(f"Context: {context}")
            
            prompt_parts.append(
                "Provide only the translation without any explanations or additional text."
            )
            prompt_parts.append(f"\nText to translate:\n{text}")
            
            prompt = "\n".join(prompt_parts)

            logger.info(f"Requesting translation to {target_language}")
            
            response = await self.client.chat.completions.create(
                model=settings.openai_text_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator. Provide accurate, natural-sounding translations."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.openai_max_tokens,
                temperature=settings.openai_temperature,
            )

            translation = response.choices[0].message.content.strip()
            logger.info("Translation completed successfully")
            return translation

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception("Translation failed. Please try again.")
        except Exception as e:
            logger.error(f"Translation error: {type(e).__name__}: {str(e)}")
            raise Exception("Translation failed. Please try again.")

    async def rephrase(
        self,
        text: str,
        language: str,
        context: Optional[str] = None
    ) -> str:
        """
        Rephrase text while maintaining meaning
        
        Args:
            text: Text to rephrase
            language: Language of the text
            context: Optional context
            
        Returns:
            Rephrased text
        """
        if not self._is_available():
            raise Exception("AI service is not configured")

        try:
            prompt_parts = [
                f"Rephrase the following {language} text while maintaining its original meaning.",
                "Make it sound more natural and fluent.",
            ]
            
            if context:
                prompt_parts.append(f"Context: {context}")
            
            prompt_parts.append(
                "Provide only the rephrased text without any explanations."
            )
            prompt_parts.append(f"\nText to rephrase:\n{text}")
            
            prompt = "\n".join(prompt_parts)

            logger.info(f"Requesting rephrase for {language} text")
            
            response = await self.client.chat.completions.create(
                model=settings.openai_text_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional text editor. Provide natural, fluent rephrasing."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.openai_max_tokens,
                temperature=settings.openai_temperature,
            )

            rephrased = response.choices[0].message.content.strip()
            logger.info("Rephrase completed successfully")
            return rephrased

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
    ) -> str:
        """
        Shorten text while preserving key meaning
        
        Args:
            text: Text to shorten
            language: Language of the text
            context: Optional context
            
        Returns:
            Shortened text
        """
        if not self._is_available():
            raise Exception("AI service is not configured")

        try:
            prompt_parts = [
                f"Shorten the following {language} text while preserving its key meaning.",
                "Make it concise and clear.",
            ]
            
            if context:
                prompt_parts.append(f"Context: {context}")
            
            prompt_parts.append(
                "Provide only the shortened text without any explanations."
            )
            prompt_parts.append(f"\nText to shorten:\n{text}")
            
            prompt = "\n".join(prompt_parts)

            logger.info(f"Requesting shorten for {language} text")
            
            response = await self.client.chat.completions.create(
                model=settings.openai_text_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional text editor. Provide concise, clear text."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.openai_max_tokens,
                temperature=settings.openai_temperature,
            )

            shortened = response.choices[0].message.content.strip()
            logger.info("Shorten completed successfully")
            return shortened

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
    ) -> list[str]:
        """
        Generate alternative variants of the text
        
        Args:
            text: Text to generate variants for
            language: Language of the text
            context: Optional context
            count: Number of variants to generate (default: 3)
            
        Returns:
            List of variant texts
        """
        if not self._is_available():
            raise Exception("AI service is not configured")

        try:
            prompt_parts = [
                f"Generate {count} alternative variants of the following {language} text.",
                "Each variant should have a slightly different tone or wording while maintaining the same meaning.",
            ]
            
            if context:
                prompt_parts.append(f"Context: {context}")
            
            prompt_parts.append(
                f"Provide exactly {count} variants, each on a new line, numbered 1., 2., 3., etc."
            )
            prompt_parts.append(f"\nText:\n{text}")
            
            prompt = "\n".join(prompt_parts)

            logger.info(f"Requesting {count} variants for {language} text")
            
            response = await self.client.chat.completions.create(
                model=settings.openai_text_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative text editor. Provide natural, varied alternatives."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.openai_max_tokens,
                temperature=1.2,  # Higher temperature for more variety
            )

            result = response.choices[0].message.content.strip()
            
            # Parse numbered list
            variants = []
            for line in result.split('\n'):
                line = line.strip()
                if not line:
                    continue
                # Remove numbering (1., 2., etc.)
                import re
                cleaned = re.sub(r'^\d+\.\s*', '', line)
                if cleaned:
                    variants.append(cleaned)
            
            logger.info(f"Generated {len(variants)} variants successfully")
            return variants[:count]  # Ensure we don't return more than requested

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise Exception("Variant generation failed. Please try again.")
        except Exception as e:
            logger.error(f"Variant generation error: {type(e).__name__}: {str(e)}")
            raise Exception("Variant generation failed. Please try again.")


# Global instance
ai_service = AIService()

