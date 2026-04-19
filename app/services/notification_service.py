import smtplib
from email.message import EmailMessage


def send_reset_notification(email: str, token: str):
    msg = EmailMessage()
    msg["Subject"] = "Password Reset"
    msg["From"] = "noreply@yourapp.com"
    msg["To"] = email

    msg.set_content(f"Use this token to reset password: {token}")

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("your_email", "your_password")
        server.send_message(msg)

def send_sms(phone: str, token: str):
    print(f"Send SMS to {phone}: {token}")