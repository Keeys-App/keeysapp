"""
Email service for sending transactional emails via Brevo API.
"""
import asyncio
import logging
import threading
from typing import Optional

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending emails via Brevo (Sendinblue) API.
    """
    
    _instance: Optional["EmailService"] = None
    _api_instance: Optional[sib_api_v3_sdk.TransactionalEmailsApi] = None
    
    def __init__(self):
        """Initialize the Brevo API client."""
        api_key = settings.brevo_api_key
        
        if not api_key:
            logger.warning("BREVO_API_KEY not configured. Email sending will be disabled.")
            self._api_instance = None
            return
        
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = api_key
        
        self._api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        logger.info("Brevo email service initialized successfully")
    
    @classmethod
    def get_instance(cls) -> "EmailService":
        """Get singleton instance of EmailService."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return self._api_instance is not None
    
    def _get_sender(self) -> dict:
        """Get sender information from settings."""
        return {
            "email": settings.brevo_sender_email,
            "name": settings.brevo_sender_name
        }
    
    def send_welcome_email(self, email: str, username: str) -> bool:
        """
        Send welcome email to newly registered user.
        
        Args:
            email: User's email address
            username: User's username
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.is_configured:
            logger.warning(f"Email service not configured. Skipping welcome email to {email}")
            return False
        
        sender = self._get_sender()
        
        # Simple text content for welcome email
        text_content = f"""Hello {username}!

Welcome to Locales App! We're excited to have you on board.

Your account has been successfully created and you can now start using the app to manage your translations and localization projects.

If you have any questions, feel free to reach out to our support team.

Best regards,
The Locales Team
"""
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender=sender,
            to=[{"email": email, "name": username}],
            subject="Welcome to Locales App!",
            text_content=text_content
        )
        
        try:
            response = self._api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Welcome email sent successfully to {email}. Message ID: {response.message_id}")
            return True
        except ApiException as e:
            # Log the error but never expose technical details
            logger.error(f"Failed to send welcome email to {email}: {type(e).__name__}")
            return False
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected error sending welcome email to {email}: {type(e).__name__}")
            return False


async def send_welcome_email_async(email: str, username: str) -> bool:
    """
    Send welcome email asynchronously (runs in thread pool).
    
    This function is designed to be called with asyncio.create_task()
    so it doesn't block the main request.
    
    Args:
        email: User's email address
        username: User's username
        
    Returns:
        True if email was sent successfully, False otherwise
    """
    loop = asyncio.get_event_loop()
    
    # Run the synchronous email sending in a thread pool
    return await loop.run_in_executor(
        None,
        lambda: EmailService.get_instance().send_welcome_email(email, username)
    )


def send_welcome_email_background(email: str, username: str) -> None:
    """
    Send welcome email in a background thread (fire and forget).
    
    This function spawns a new thread to send the email,
    allowing the caller to return immediately without waiting.
    Safe to call from synchronous code.
    
    Args:
        email: User's email address
        username: User's username
    """
    def _send():
        try:
            EmailService.get_instance().send_welcome_email(email, username)
        except Exception as e:
            # Log but never crash - this is background task
            logger.error(f"Background email send failed for {email}: {type(e).__name__}")
    
    thread = threading.Thread(target=_send, daemon=True)
    thread.start()
    logger.info(f"Welcome email background thread started for {email}")

