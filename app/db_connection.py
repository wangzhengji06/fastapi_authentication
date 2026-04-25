from functools import lru_cache

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./database.db"


@lru_cache
def get_engine():
    engine = create_engine(DATABASE_URL)

    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def get_session():
    Session = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    try:
        session = Session()
        yield session
    finally:
        session.close()
