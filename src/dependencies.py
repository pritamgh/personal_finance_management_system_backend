from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config import Config

# Database Setup
engine = create_engine(Config.POSTGRESQLDB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Dependency that provides a session to interact with the database.
    The session is automatically closed when the request is finished.

    This is a FastAPI dependency that will be injected into route functions
    where database access is required.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# OAuth2 for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
