from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./database.db"


@lru_cache
def get_engine():
    return create_engine(DATABASE_URL)


def get_session():
    Session = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    try:
        session = Session()
        yield session
    finally:
        session.close()
