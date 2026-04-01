from db_connection import get_session
from exceptions import UserAlreadyExists
from fastapi import APIRouter, Depends, status
from models import Role
from operations import add_user
from responses import (
    ResponseAdminUser,
    ResponseCreateUser,
    UserCreateBody,
    UserCreateResponse,
)
from security import require_role
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/register/premium-user",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseCreateUser,
    responses={
        status.HTTP_409_CONFLICT: {"description": "The user already exists"},
        status.HTTP_201_CREATED: {"description": "User created"},
    },
)
def register_premium_user(
    user: UserCreateBody,
    session: Session = Depends(get_session),
):
    created_user = add_user(
        session=session,
        **user.model_dump(),
        role=Role.admin,
    )
    if not created_user:
        raise UserAlreadyExists()

    user_response = UserCreateResponse(
        username=created_user.username,
        email=created_user.email,
    )
    return {
        "message": "user created",
        "user": user_response,
    }


@router.get(
    "/admin",
    response_model=ResponseAdminUser,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Not Authorized"},
    },
)
def admin(
    current_user=Depends(require_role(Role.admin)),
):
    return ResponseAdminUser(message=f"Welcome, admin {current_user.username}.")
