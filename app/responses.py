from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class UserCreateBody(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserCreateResponse(BaseModel):
    username: str
    email: EmailStr


class ResponseCreateUser(BaseModel):
    message: Annotated[str, Field(default="user created")]
    user: UserCreateResponse


class UserLoginBody(BaseModel):
    email: EmailStr
    password: str


class ResponseProfileUser(BaseModel):
    id: str
    email: EmailStr
    username: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class ResponseAdminUser(BaseModel):
    message: str

