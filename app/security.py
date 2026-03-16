from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from db_connection import get_session
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from models import Role
from operations import get_user, pwd_context
from responses import ResponseProfileUser, TokenResponse, UserLoginBody
from sqlalchemy.orm import Session

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_SECONDS = os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS")


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
    payload = {"sub": subject, "exp": expire, "role": Role}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str, session: Session):
    """
    Decode JWT and fetch the user.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
    except JWTError:
        return None

    if not subject:
        return None

    return get_user(session, subject)


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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(subject=user.email, role=user.role)
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_SECONDS,
    }


@router.get(
    "/profile",
    response_model=ResponseProfileUser,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Not Authorized"},
    },
)
def profile(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    session: Session = Depends(get_session),
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized"
        )

    user = decode_access_token(credentials.credentials, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized"
        )

    return ResponseProfileUser(
        id=str(user.id),
        email=user.email,
        username=user.username,
    )
