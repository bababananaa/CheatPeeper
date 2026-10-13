
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# load .env file thats next to this py file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from backend/.env")

# create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# factory that creates new database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# creates session, makes it available to calling code, and closes it when it ends
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()