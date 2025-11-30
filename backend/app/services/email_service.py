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
from app.services.email_template_service import EmailTemplateService

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
        
        # Render template with variables
        template_service = EmailTemplateService.get_instance()
        template = template_service.render("welcome", {
            "username": username,
            "app_name": settings.brevo_sender_name,
        })
        
        if not template:
            logger.error(f"Failed to render welcome email template for {email}")
            return False
        
        return self._send_email(
            to_email=email,
            to_name=username,
            subject=template.subject,
            text_content=template.text_content,
            html_content=template.html_content
        )

    def send_team_invitation_email(
        self,
        email: str,
        team_name: str,
        inviter_name: str,
        invite_code: str,
        role: str
    ) -> bool:
        """
        Send team invitation email.
        
        Args:
            email: Recipient's email address
            team_name: Name of the team
            inviter_name: Name of the person who sent the invitation
            invite_code: Invitation code (UUID)
            role: Role being offered
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.is_configured:
            logger.warning(f"Email service not configured. Skipping invitation email to {email}")
            return False
        
        # Build invite URL
        invite_url = f"{settings.app_url}/invite/{invite_code}"
        
        # Render template with variables
        template_service = EmailTemplateService.get_instance()
        template = template_service.render("team_invitation", {
            "team_name": team_name,
            "inviter_name": inviter_name,
            "invite_url": invite_url,
            "role": role,
            "app_name": settings.brevo_sender_name,
        })
        
        if not template:
            logger.error(f"Failed to render team invitation email template for {email}")
            return False
        
        return self._send_email(
            to_email=email,
            to_name=email,  # We may not know their name yet
            subject=template.subject,
            text_content=template.text_content,
            html_content=template.html_content
        )
    
    def _send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        text_content: str,
        html_content: Optional[str] = None
    ) -> bool:
        """
        Send an email via Brevo API.
        
        Args:
            to_email: Recipient email address
            to_name: Recipient name
            subject: Email subject
            text_content: Plain text content
            html_content: Optional HTML content
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        sender = self._get_sender()
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender=sender,
            to=[{"email": to_email, "name": to_name}],
            subject=subject,
            text_content=text_content,
            html_content=html_content
        )
        
        try:
            response = self._api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email sent successfully to {to_email}. Message ID: {response.message_id}")
            return True
        except ApiException as e:
            # Log the error but never expose technical details
            logger.error(f"Failed to send email to {to_email}: {type(e).__name__}")
            return False
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected error sending email to {to_email}: {type(e).__name__}")
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


def send_team_invitation_email_background(
    email: str,
    team_name: str,
    inviter_name: str,
    invite_code: str,
    role: str
) -> None:
    """
    Send team invitation email in a background thread (fire and forget).
    
    Args:
        email: Recipient's email address
        team_name: Name of the team
        inviter_name: Name of the person who sent the invitation
        invite_code: Invitation code (UUID)
        role: Role being offered
    """
    def _send():
        try:
            EmailService.get_instance().send_team_invitation_email(
                email=email,
                team_name=team_name,
                inviter_name=inviter_name,
                invite_code=invite_code,
                role=role
            )
        except Exception as e:
            # Log but never crash - this is background task
            logger.error(f"Background invitation email send failed for {email}: {type(e).__name__}")
    
    thread = threading.Thread(target=_send, daemon=True)
    thread.start()
    logger.info(f"Team invitation email background thread started for {email}")

