import os
import smtplib
from email.message import EmailMessage

from auth import VERIFICATION_CODE_EXPIRE_MINUTES


def send_verification_email(to: str, code: str) -> None:
    smtp_host = os.getenv("SMTP_HOST")

    # no SMTP configured (local dev): print the code instead of emailing it
    if not smtp_host:
        print(f"[dev] verification code for {to}: {code}")
        return

    message = EmailMessage()
    message["Subject"] = "Your verification code"
    # `or` rather than a getenv default, since a blank SMTP_FROM= in .env is "" not missing
    message["From"] = os.getenv("SMTP_FROM") or os.getenv("SMTP_USER")
    message["To"] = to
    message.set_content(
        f"Your verification code is {code}. It expires in {VERIFICATION_CODE_EXPIRE_MINUTES} minutes."
    )

    with smtplib.SMTP(smtp_host, int(os.getenv("SMTP_PORT", "587"))) as server:
        server.starttls()
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
        server.send_message(message)
