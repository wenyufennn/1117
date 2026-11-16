import os
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, status
from .config import JWT_SECRET

SECRET_KEY = JWT_SECRET or "super_secret_jwt_key_123456"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day


def get_password_hash(password: str) -> str:
    salt = "pj_salt_2026"
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"pbkdf2:sha256${salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if plain_password == hashed_password:
        return True
    if hashed_password.startswith("pbkdf2:sha256$"):
        parts = hashed_password.split("$")
        if len(parts) == 3:
            salt = parts[1]
            expected_hex = parts[2]
            key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return hmac.compare_digest(key.hex(), expected_hex)
    return plain_password == hashed_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="憑證無效或已過期，請重新登入",
        )
