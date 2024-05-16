from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
import redis.asyncio as redis

from auth.model import User
import auth.schemas as schemas
from auth.utils import (
    generate_auth_code,
    generate_invite_code,
    create_access_token,
    create_refresh_token,
)
from auth.deps import get_current_user
from config import settings
from database.db import async_session_factory
from referal.utils import form_user_profile, correct_phone_number


r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

router = APIRouter(tags=['referal'])

templates = Jinja2Templates(directory='templates')


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def get_register_code(phone_number: schemas.UserCreate) -> None:
    """Регистрация пользователя."""

    async with async_session_factory() as session:
        user_phone_number = await correct_phone_number(phone_number.phone_number)
        query = select(User).filter_by(phone_number=user_phone_number)
        query_result = await session.execute(query)
        db_user = query_result.first()
        if not db_user:
            invite_code = await generate_invite_code()
            user = User(phone_number=user_phone_number, invite_code=invite_code)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        auth_code = await generate_auth_code()
        await r.set(user_phone_number, auth_code, ex=300)
        print(auth_code)


@router.post('/login', status_code=status.HTTP_200_OK)
async def login(user_to_login: schemas.UserToLogin) -> schemas.Token:
    """Получение access кода для пользователя."""

    user_phone_number = await correct_phone_number(user_to_login.phone_number)
    if await r.get(user_phone_number) == user_to_login.auth_code:
        async with async_session_factory() as session:
            query = select(User).filter_by(phone_number=user_phone_number)
            query_result = await session.execute(query)
            user_db: User | None = query_result.scalars().first()
            if not user_db:
                raise HTTPException(status_code=404, detail='User dosent exist')
            token = {
                'access_token': await create_access_token(
                    data={'sub': user_db.phone_number}
                ),
                'refresh_token': await create_refresh_token(
                    data={'sub': user_db.phone_number}
                ),
            }
            return token
    raise HTTPException(status_code=404, detail='User dosent exist')


@router.get('/me', status_code=status.HTTP_200_OK)
async def me(user: User = Depends(get_current_user)) -> schemas.User:
    """Профиль пользователя."""

    user_to_return = await form_user_profile(user)
    return user_to_return


@router.post('/invite', status_code=status.HTTP_201_CREATED)
async def use_invite_code(
    invite_code: schemas.InviteCode,
    user: User = Depends(get_current_user),
) -> schemas.User:
    """Применение реферального кода."""

    if user.used_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Invite code was already used'
        )
    if user.invite_code == invite_code.invite_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cannot use the same code as yours',
        )
    async with async_session_factory() as session:
        query = select(User).filter_by(invite_code=invite_code.invite_code)
        query_result = await session.execute(query)
        db_user_with_invite_code = query_result.scalars().first()
        if not db_user_with_invite_code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='Invite code doesnt exist'
            )
        await session.commit()
        user.used_code = invite_code.invite_code
        session.add(user)
        await session.commit()
        await session.refresh(user)
        user_to_return = await form_user_profile(user)
        return user_to_return


@router.get('/', response_class=HTMLResponse, include_in_schema=False)
async def main_page(request: Request):
    return templates.TemplateResponse(request=request, name='index.html')


@router.get('/profile', response_class=HTMLResponse, include_in_schema=False)
async def profile_page(request: Request):
    return templates.TemplateResponse(request=request, name='profile.html')
