from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite for easy setup (file-based DB, no password/host issues)
SQLALCHEMY_DATABASE_URL = "sqlite:///./pvdb.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()