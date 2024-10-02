from fastapi_mail import FastMail, ConnectionConfig, MessageSchema
from settings import settings

# at the instance of mail all the configuration is done and importing it from settings
mail_config = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_FROM_NAME= settings.MAIL_FROM_NAME, 
    MAIL_STARTTLS = settings.MAIL_STARTTLS,
    MAIL_SSL_TLS = settings.MAIL_SSL_TLS,
    USE_CREDENTIALS = settings.USE_CREDENTIALS,
    VALIDATE_CERTS = settings.VALIDATE_CERTS,
)

# Sending the verification mail when new user register using api
# In this function it takes email and verify link : str (argument)  

async def send_verification_email(email: str, verify_link: str):
  
    # Send verification email
    message = MessageSchema(
        subject= "FundooNotes - Verify your email",
        recipients= [email],
        body= f"Click on the link to verify your email: {verify_link}",
        subtype= "html"
    )

    # mail object fm is assigned FastMail with configuration object as parameter
    fm = FastMail(mail_config)
    await fm.send_message(message)