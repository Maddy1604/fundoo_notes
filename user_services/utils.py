from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def get_hash_password(password):
    return bcrypt_context.hash(password)
