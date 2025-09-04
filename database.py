from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

SQLITE_DATABASE_URL = "sqlite:///./store.db"

engine = create_engine(
    SQLITE_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)


