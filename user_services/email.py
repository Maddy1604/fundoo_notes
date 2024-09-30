from fastapi_mail import FastMail, ConnectionConfig, MessageSchema
from settings import settings


mail_config = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = "no-reply@example.com",
    MAIL_PORT = 2525,
    MAIL_SERVER = "smtp.mailtrap.io",
    MAIL_FROM_NAME= "FundooNotes", #.env
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
)

async def send_verification_email(email: str, token: str, url: str):
    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=f"Click on the link to verify your account: {url}",
        subtype="html"
    )
    fm = FastMail(mail_config)
    await fm.send_message(message)