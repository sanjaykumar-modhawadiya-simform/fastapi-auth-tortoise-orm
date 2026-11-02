"""
Security Utilities Module.

Provides cryptographic helpers for hashing passwords using native bcrypt
and generating/verifying JWT tokens using PyJWT.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
import jwt
from app.config import settings


def hash_password(password: str) -> str:
    """
    Hashes a plain text password using native bcrypt.
    """
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a hashed password using native bcrypt.
    """
    try:
        pwd_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Encodes data payload into a signed JWT access token using PyJWT.

    :param data: Claims data to encode in payload.
    :param expires_delta: Custom token expiration duration.
    :return: Signed JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
