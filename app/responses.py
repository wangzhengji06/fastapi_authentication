from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, StringConstraints


class UserCreateBody(BaseModel):
    username: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    email: EmailStr
    password: str


class UserCreateResponse(BaseModel):
    username: str
    email: EmailStr


class ResponseCreateUser(BaseModel):
    message: Annotated[str, Field(default="user created")]
    user: UserCreateResponse


class ProjectCreateBody(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ProjectCreateResponse(BaseModel):
    id: int
    name: str


class ResponseCreateProject(BaseModel):
    message: Annotated[str, Field(default="project created")]
    project: ProjectCreateResponse


class TaskCreateBody(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class TaskCreateResponse(BaseModel):
    id: int
    title: str


class ResponseCreateTask(BaseModel):
    message: Annotated[str, Field(default="task created")]
    task: TaskCreateResponse


class UserLoginBody(BaseModel):
    email: EmailStr
    password: str


class ResponseProfileUser(BaseModel):
    id: int
    email: EmailStr
    username: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class ResponseAdminUser(BaseModel):
    message: str
