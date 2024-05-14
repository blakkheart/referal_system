from typing import Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    phone_number: str = Field(
        pattern=r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$'
    )


class User(BaseModel):
    phone_number: str = Field(
        pattern=r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$'
    )
    invite_code: str = Field(max_length=6)
    used_code: Optional[str] = None
    list_of_refferals: Optional[list[str]] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    phone_number: str = Field(
        pattern=r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$'
    )


class UserToLogin(UserCreate):
    auth_code: str = Field(max_length=4)


class InviteCode(BaseModel):
    invite_code: str = Field(max_length=6)
