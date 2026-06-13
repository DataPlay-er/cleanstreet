# SQLModel engine + get_session (same pattern as auth)

from sqlmodel import SQLModel, create_engine, session
from collections.abc import Generator
from detection.config import settings

engine = create_engine(
    settings.database_url,
    echo = settings.debug,
    pool_pre_ping = True,
    pool_size = 5,
    max_overflow = 10,
)

def create_db_and_tables() -> None:
    SQLModel.metedata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session