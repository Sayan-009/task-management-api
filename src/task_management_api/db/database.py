from sqlalchemy import URL, create_engine

from task_management_api.core.config import settings

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.database_user,
    password=settings.database_password,
    host=settings.database_host,
    port=settings.database_port,
    database=settings.database_name,
)


engine = create_engine(DATABASE_URL)




