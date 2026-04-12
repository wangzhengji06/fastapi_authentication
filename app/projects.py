from db_connection import get_session
from fastapi import APIRouter, Depends, status
from models import Project, User
from operations import (
    add_project,
    add_task,
    get_project_for_user,
    list_projects_for_user,
    list_tasks_for_project,
)
from responses import (
    ProjectCreateBody,
    ProjectResponse,
    ResponseCreateProject,
    ResponseCreateTask,
    TaskCreateBody,
    TaskResponse,
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


def get_owned_project(
    project_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Project:
    return get_project_for_user(session=session, user=user, project_id=project_id)


@router.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
)
def get_project(project: Project = Depends(get_owned_project)) -> ProjectResponse:
    return ProjectResponse(id=project.id, name=project.name)


@router.post(
    "/projects/{project_id}/tasks",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseCreateTask,
)
def create_task(
    task: TaskCreateBody,
    project: Project = Depends(get_owned_project),
    session: Session = Depends(get_session),
) -> ResponseCreateTask:
    db_task = add_task(session=session, project=project, **task.model_dump())

    return ResponseCreateTask(
        message="task created",
        task=TaskResponse(
            id=db_task.id,
            title=db_task.title,
        ),
    )


@router.get(
    "/projects/{project_id}/tasks",
    response_model=list[TaskResponse],
)
def list_tasks(
    project: Project = Depends(get_owned_project),
    session: Session = Depends(get_session),
) -> list[TaskResponse]:
    tasks = list_tasks_for_project(session=session, project=project)
    return [TaskResponse(id=task.id, title=task.title) for task in tasks]
