from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from settings import settings
import jwt
import logging


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")



def get_hash_password(password):
    return bcrypt_context.hash(password)

def verify_password(plain_password, hased_password):
    return bcrypt_context.verify(plain_password, hased_password)

def create_token(data: dict, token_type: str, exp= None):
    
    if token_type == "access":
        expiration = exp or (datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY))
    elif token_type == "refresh":
        expiration = exp or (datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRY))
    else:
        raise ValueError("Invalid token type. Must be 'access' or 'refresh'.")

    return jwt.encode({**data, "exp": expiration}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

# To generate both tokens
def create_tokens(data: dict):
    """
    Generates both access and refresh tokens.
    """
    access_token = create_token(data, "access")
    refresh_token = create_token(data, "refresh")
    return access_token, refresh_token

def decode_token(token):
    try:
        token_data = jwt.decode(
            jwt=token,
            key=settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM] 
        )

        return token_data
    
    except Exception as error:
        logging.exception(error)
        return None
