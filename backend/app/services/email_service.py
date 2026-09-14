"""
Email delivery service.

If EMAIL_ENABLED is False (the default for local/dev), emails are
logged instead of sent — so the auth flow is fully testable without an
SMTP server. Swap in a real provider (SES, SendGrid, etc.) here without
touching any calling code.
"""
import smtplib
from email.message import EmailMessage

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    def _send(self, to: str, subject: str, body: str) -> None:
        if not settings.EMAIL_ENABLED:
            logger.info("EMAIL[disabled] to=%s subject=%r body=%s", to, subject, body)
            return

        msg = EmailMessage()
        msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

    def send_verification_email(self, to: str, token: str) -> None:
        link = f"{settings.FRONTEND_URL}verify-email?token={token}"
        self._send(
            to=to,
            subject="Verify your InterviewIQ AI account",
            body=f"Welcome to InterviewIQ AI!\n\nVerify your email:\n{link}\n\n"
            f"This link expires in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} hours.",
        )

    def send_password_reset_email(self, to: str, token: str) -> None:
        link = f"{settings.FRONTEND_URL}reset-password?token={token}"
        self._send(
            to=to,
            subject="Reset your InterviewIQ AI password",
            body=f"We received a request to reset your password.\n\n{link}\n\n"
            f"This link expires in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes. "
            f"If you didn't request this, you can safely ignore this email.",
        )


email_service = EmailService()
