from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

# Since we are using standard PostgreSQL, psycopg2 is used.
# If we need sqlite for fallback/local testing easily, we can detect it, but user explicitly asked for PostgreSQL.
DATABASE_URL = settings.DATABASE_URL

# For PostgreSQL or SQLite (if it starts with sqlite, add connect_args)
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
