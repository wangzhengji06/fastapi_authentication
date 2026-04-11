from contextlib import asynccontextmanager

import premium_access
import projects
import security
from db_connection import get_engine, get_session
from exceptions import (
    InvalidCredentials,
    PermissionDenied,
    ProjectNotFound,
    UserAlreadyExists,
)
from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models import Base
from operations import (
    add_user,
)
from responses import (
    ResponseCreateUser,
    UserCreateBody,
    UserCreateResponse,
)
from sqlalchemy.orm import Session


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=get_engine())
    yield


app = FastAPI(title="Userapp", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(InvalidCredentials)
async def handle_invalid_credentials(request, exc: InvalidCredentials):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": exc.error_code,
            "message": exc.message,
        },
    )


@app.exception_handler(PermissionDenied)
async def handle_permission_denied(request, exc: PermissionDenied):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": exc.error_code,
            "message": exc.message,
        },
    )


@app.exception_handler(UserAlreadyExists)
async def handle_user_already_exists(request, exc: UserAlreadyExists):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": exc.error_code,
            "message": exc.message,
        },
    )


@app.exception_handler(ProjectNotFound)
async def project_not_found_handler(request, exc: ProjectNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
        },
    )


app.include_router(security.router)
app.include_router(premium_access.router)
app.include_router(projects.router)


@app.post(
    "/register/user",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseCreateUser,
    responses={status.HTTP_409_CONFLICT: {"description": "The user already exists"}},
)
def register(
    user: UserCreateBody, session: Session = Depends(get_session)
) -> dict[str, UserCreateResponse]:
    user = add_user(session=session, **user.model_dump())
    if not user:
        raise UserAlreadyExists()
    user_response = UserCreateResponse(username=user.username, email=user.email)
    return {"message": "user created", "user": user_response}
