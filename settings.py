from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file='.env', extra="ignore")

    db_url : str
    notes_db_url : str
    JWT_SECRET : str
    JWT_ALGORITHM : str
    ACCESS_TOKEN_EXPIRY : int
    REFRESH_TOKEN_EXPIRY : int
    MAIL_USERNAME : str
    MAIL_PASSWORD : str
    MAIL_FROM : str
    MAIL_PORT : int
    MAIL_SERVER : str
    MAIL_FROM_NAME : str
    MAIL_STARTTLS : bool = True
    MAIL_SSL_TLS : bool = False
    USE_CREDENTIALS : bool = True
    VALIDATE_CERTS : bool = True
settings = Settings()