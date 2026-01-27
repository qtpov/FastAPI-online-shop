import bcrypt

import jwt
from datetime import datetime, timedelta
from app.core.config import settings

JWT_SECRET = settings.JWT_SECRET
JWT_EXPIRE_MINUTES = settings.JWT_EXPIRE_MINUTES
JWT_REFRESH_EXPIRE_DAYS = settings.JWT_REFRESH_EXPIRE_DAYS

def hash_password(password: str) -> str:
    # bcrypt ограничивает пароль 72 байтами
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def create_access_token(user_id: int, role: str = "user") -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
        "role": role,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token

def create_refresh_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")