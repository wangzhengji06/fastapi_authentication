from db_connection import get_session
from fastapi import APIRouter, Depends, status
from models import User
from operations import (
    add_project,
    get_project_for_user,
    list_projects_for_user,
)
from responses import (
    ProjectCreateBody,
    ProjectResponse,
    ResponseCreateProject,
)
from security import get_current_user
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/projects",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseCreateProject,
)
def create_project(
    project: ProjectCreateBody,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ResponseCreateProject:
    db_project = add_project(session=session, user=user, **project.model_dump())

    return ResponseCreateProject(
        message="project created",
        project=ProjectResponse(
            id=db_project.id,
            name=db_project.name,
        ),
    )


@router.get(
    "/projects",
    response_model=list[ProjectResponse],
)
def list_projects(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[ProjectResponse]:
    projects = list_projects_for_user(session=session, user=user)
    return [ProjectResponse(id=project.id, name=project.name) for project in projects]


@router.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ProjectResponse:
    project = get_project_for_user(session=session, user=user, project_id=project_id)
    return ProjectResponse(id=project.id, name=project.name)
