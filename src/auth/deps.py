from datetime import datetime

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from pydantic import ValidationError
from sqlalchemy import select
from jose import jwt, JWTError

from auth.model import User
import auth.schemas as schemas
from auth.utils import JWT_SECRET_KEY, ALGORITHM
from database.db import async_session_factory


class JWTBearer(HTTPBearer):
    """Класс для обработки JWT токена."""

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(
            request
        )
        if credentials:
            if not credentials.scheme == 'Bearer':
                raise HTTPException(
                    status_code=403, detail='Invalid authentication scheme.'
                )
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail='Invalid authorization code.')


async def get_current_user(token: str = Depends(JWTBearer())) -> User:
    """Вспомогательная функция для получения пользователя и проверки JWT токена."""

    async with async_session_factory() as session:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
            phone_number: str = payload.get('sub')
            if phone_number is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Could not validate credentials',
                    headers={'WWW-Authenticate': 'Bearer'},
                )
            token_data = schemas.TokenData(phone_number=phone_number)
            if datetime.fromtimestamp(payload.get('exp')) < datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Token expired',
                    headers={'WWW-Authenticate': 'Bearer'},
                )
        except (JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Could not validate credentials',
                headers={'WWW-Authenticate': 'Bearer'},
            )
        query = select(User).filter_by(phone_number=token_data.phone_number)
        db_user = await session.execute(query)
        user_to_login = db_user.scalars().first()
        if not user_to_login:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='Could not find user'
            )
        return user_to_login
