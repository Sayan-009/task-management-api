from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine

from task_management_api.core.config import settings

DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.database_user,
    password=settings.database_password,
    host=settings.database_host,
    port=settings.database_port,
    database=settings.database_name,
)


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)




