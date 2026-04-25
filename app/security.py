from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from db_connection import get_session
from dotenv import load_dotenv
from exceptions import InvalidCredentials, PermissionDenied
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from models import Role
from operations import get_user, pwd_context
from responses import ResponseProfileUser, TokenResponse, UserLoginBody
from sqlalchemy.orm import Session

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS"))


router = APIRouter()

bearer_scheme = HTTPBearer(auto_error=False)


def authenticate_user(session: Session, email: str, password: str):
    """
    Authenticate using email + password
    """
    user = get_user(session, email)
    print(f"The user I got is {user}.")
    if not user:
        return None
    if not pwd_context.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(subject: str, role: Role) -> str:
    """
    subject will be stored in the JWT `sub` claim.
    Here we store the user's email to match the assignment flow.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    payload = {"sub": subject, "exp": expire, "role": role}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    session: Session = Depends(get_session),
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise InvalidCredentials()

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise InvalidCredentials()

    subject = payload.get("sub")
    if not subject:
        raise InvalidCredentials()

    user = get_user(session, subject)
    if not user:
        raise InvalidCredentials()

    return user


def require_role(required_role: Role):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role != required_role:
            raise PermissionDenied()
        return current_user

    return role_checker


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Incorrect email or password"}
    },
)
def login(
    body: UserLoginBody,
    session: Session = Depends(get_session),
):
    user = authenticate_user(session=session, **body.model_dump())
    if not user:
        raise InvalidCredentials()

    token = create_access_token(subject=user.email, role=user.role)
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_SECONDS,
    }


@router.get(
    "/profile",
    response_model=ResponseProfileUser,
)
def profile(current_user=Depends(get_current_user)):
    return ResponseProfileUser(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
    )
