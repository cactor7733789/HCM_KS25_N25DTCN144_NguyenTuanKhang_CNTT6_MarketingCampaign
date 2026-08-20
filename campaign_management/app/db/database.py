from sqlalchemy.orm import sessionmaker,DeclarativeBase
from sqlalchemy import create_engine
from app.core.config import settings

database_url = DATABASE_URL = settings.DATABASE_URL

engine = create_engine(database_url)

SessionLocal = sessionmaker(
    autoflush= False,
    autocommit = False,
    bind=engine
)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

