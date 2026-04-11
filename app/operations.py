from typing import List

from exceptions import ProjectNotFound
from models import Project, Role, Task, User
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# IntegrityError will take into account the attempt to add a username and emails that already exists.
def add_user(
    session: Session,
    username: str,
    password: str,
    email: str,
    role: Role = Role.user,
) -> User | None:
    hashed_password = pwd_context.hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role,
    )
    session.add(db_user)
    try:
        session.commit()
        session.refresh(db_user)
    except IntegrityError:
        session.rollback()
        return
    return db_user


def get_user(
    session: Session,
    email: str,
) -> User | None:
    user = session.query(User).filter(User.email == email).first()
    return user


def add_project(
    session: Session,
    user: User,
    name: str,
) -> Project:
    db_project = Project(name=name, user_id=user.id)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project


def get_project_for_user(
    session: Session,
    user: User,
    project_id: int,
) -> Project:
    project = (
        session.query(Project)
        .filter(Project.user_id == user.id)
        .filter(Project.id == project_id)
        .first()
    )
    if not project:
        raise ProjectNotFound()
    return project


def list_projects_for_user(
    session: Session,
    user: User,
) -> List[Project]:
    projects = session.query(Project).filter(Project.user_id == user.id).all()
    return projects


def add_task(
    session: Session,
    project: Project,
    title: str,
) -> Task:
    db_task = Task(title=title, project_id=project.id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


def list_tasks_for_project(
    session: Session,
    project: Project,
) -> List[Task]:
    tasks = session.query(Task).filter(Task.project_id == project.id).all()
    return tasks
