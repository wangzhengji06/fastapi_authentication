from models import Role, User
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
    role: Role = Role.basic,
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


def get_user(session: Session, email: str) -> User | None:
    user = session.query(User).filter(User.email == email).first()
    return user
