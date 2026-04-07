"""Security utilities for password hashing and JWT token management."""
import hashlib
import hmac
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from src.config import settings

# --- Password hashing using Python's built-in hashlib (PBKDF2-HMAC-SHA256)
# No C extensions, no platform issues.

def hash_password(password: str) -> str:
    """Hash a password with PBKDF2-HMAC-SHA256 + random salt."""
    salt = os.urandom(16).hex()
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260000)
    return f"{salt}${dk.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a PBKDF2 hash."""
    try:
        salt, dk_hex = hashed_password.split("$", 1)
        dk = hashlib.pbkdf2_hmac("sha256", plain_password.encode(), salt.encode(), 260000)
        return hmac.compare_digest(dk.hex(), dk_hex)
    except Exception:
        return False

# --- JWT token management

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
