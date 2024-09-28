from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def get_hash_password(password):
    return bcrypt_context.hash(password)

def verify_password(plain_password:str, hased_password:str) -> bool:
    return bcrypt_context.verify(plain_password, hased_password)
