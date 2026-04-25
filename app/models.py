from enum import Enum

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


project_shares = Table(
    "project_shares",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "project_id", ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Role(str, Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    role: Mapped[Role] = mapped_column(default=Role.user)
    projects: Mapped[list["Project"]] = relationship(
        cascade="all, delete-orphan", back_populates="user"
    )
    shared_projects: Mapped[list["Project"]] = relationship(
        secondary=project_shares, back_populates="shared_users"
    )


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped["User"] = relationship(back_populates="projects")
    tasks: Mapped[list["Task"]] = relationship(
        cascade="all, delete-orphan", back_populates="project"
    )
    shared_users: Mapped[list["User"]] = relationship(
        secondary=project_shares, back_populates="shared_projects"
    )


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    project: Mapped["Project"] = relationship(back_populates="tasks")
