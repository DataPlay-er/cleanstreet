from sqlmodel import SQLModel, create_engine, Session
from app.config import settings
from collections.abc import Generator


# Create the SQLAlchemy engine using the database URL from settings
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Check connections before using them
    connect_args={"connect_timeout": 10},  # Optional: set a connection timeout   
)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    The `with` block guarantees the session is closed even if the route
    raises an exception — no leaked connections. 
    """
    with Session(engine) as session:
        yield session

def init_db() -> None:
    """
    Creates all tables defined by SQLModel models.
 
    ONLY called during development startup or in tests.
    In production, Alembic migrations manage the schema — never call this.
    """
    SQLModel.metadata.create_all(engine)