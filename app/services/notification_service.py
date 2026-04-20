import smtplib
from email.message import EmailMessage
from app.core.config import settings


def send_reset_notification(email: str, token: str):
    msg = EmailMessage()
    msg["Subject"] = "Password Reset"
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = email

    msg.set_content(f"Use this token to reset password: {token}")

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)

def send_sms(phone: str, token: str):
    # Todo: Implement actual SMS sending logic using an SMS gateway API
    print(f"Send SMS to {phone}: {token}")