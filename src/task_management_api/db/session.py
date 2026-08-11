from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from task_management_api.db.database import engine


SessionFactory = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    session = SessionFactory()

    try:
        yield session
    finally:
        session.close()