"""
Password hashing utilities, backed by Argon2 (via passlib) with bcrypt
as a fallback scheme so existing bcrypt hashes keep verifying if the
project ever migrates from one to the other.
"""
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    default="argon2",
    deprecated="auto",
)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """True if the stored hash was made with an outdated scheme/params."""
    return pwd_context.needs_update(hashed_password)
