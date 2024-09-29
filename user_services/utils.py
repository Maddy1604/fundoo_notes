from passlib.context import CryptContext
from datetime import timedelta, datetime
from settings import settings
import jwt
import logging
from dotenv import dotenv_values


config_credentials = dotenv_values(".env")


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

ACCESS_TOKEN_EXPIRY = 3600

def get_hash_password(password):
    return bcrypt_context.hash(password)

def verify_password(plain_password, hased_password):
    return bcrypt_context.verify(plain_password, hased_password)

def create_access_token(user_data:dict, expiry:timedelta = None, refresh : bool = False):
    payload = {}

    payload['user'] =   user_data
    payload['exp'] = datetime.now() + (expiry if expiry is not None else timedelta(seconds= ACCESS_TOKEN_EXPIRY))
    payload['refresh'] = refresh

    token = jwt.encode( 
        payload = payload,
        key = settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM

    )

    return token

def decode_token(token):
    try:
        token_data = jwt.decode(
            jwt=token,
            key=settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM] 
        )

        return token_data
    
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None
