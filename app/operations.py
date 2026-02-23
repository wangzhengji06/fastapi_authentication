from email_validator import EmailNotValidError, validate_email
from models import User
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
) -> User | None:
    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, email=email, hashed_password=hashed_password)
    session.add(db_user)
    try:
        session.commit()
        session.refresh(db_user)
    except IntegrityError:
        session.rollback()
        return
    return db_user


def get_user(session: Session, username_or_email: str) -> User | None:
    try:
        validate_email(username_or_email)
        query_filter = User.email
    except EmailNotValidError:
        query_filter = User.username
    user = session.query(User).filter(query_filter == username_or_email).first()
    return user
