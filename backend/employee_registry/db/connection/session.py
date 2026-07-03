from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from employee_registry.config import get_settings


class SessionManager:
    """
    A class that implements the necessary functionality for working with the database:
    issuing sessions, storing and updating connection settings.
    """

    def __init__(self) -> None:
        self.refresh()

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(SessionManager, cls).__new__(cls)
        return cls.instance

    def get_session_maker(self) -> sessionmaker:
        return sessionmaker(
            self.engine,
            class_=Session,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    def refresh(self) -> None:
        settings = get_settings()
        self.engine = create_engine(
            settings.database_uri, 
            echo=True, 
            future=True,
            pool_size=settings.DB_POOL_SIZE,
            pool_recycle=settings.DB_CONNECT_RETRY,
        )


def get_session() -> Session:
    session_maker = SessionManager().get_session_maker()
    with session_maker() as session:
        yield session


__all__ = [
    "get_session",
]
