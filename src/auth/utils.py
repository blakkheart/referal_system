from datetime import datetime, timedelta, timezone
import secrets
import string

from sqlalchemy import select
from jose import jwt

from auth.model import User
from config import settings
from database.db import async_session_factory


ACCESS_TOKEN_EXPIRE_MINUTES = 6000
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
ALGORITHM = 'HS256'
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY


async def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Функция создания access токена."""

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Функция создания refresh токена."""

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=REFRESH_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def generate_invite_code() -> str:
    """Функция создания реферального кода."""

    characters: str = string.ascii_letters + string.digits
    invite_code: str = ''.join(secrets.choice(characters) for _ in range(6))
    async with async_session_factory() as session:
        query = select(User).filter_by(invite_code=invite_code)
        query_result = await session.execute(query)
        db_user = query_result.first()
        while db_user:
            invite_code: str = ''.join(secrets.choice(characters) for _ in range(6))
            query = select(User).filter_by(invite_code=invite_code)
            query_result = await session.execute(query)
            db_user = query_result.first()
        return invite_code


async def generate_auth_code() -> str:
    """Функция создания кода аутентификации для регистрации."""

    digits: str = string.digits
    auth_code: str = ''.join(secrets.choice(digits) for _ in range(4))
    return auth_code
