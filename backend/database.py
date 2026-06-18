from sqlalchemy import create_engine
from pathlib import Path
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# places database in project root
baseDir = Path(__file__).parent.parent
databaseURL = f"sqlite:///{baseDir}/fieldservice.db"

# Connects to database
engine = create_engine(databaseURL, connect_args={"check_same_thread": False})

# each request gets its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#This will tell SQLAchemy to track all tables
class Base(DeclarativeBase):
    pass

# dependency function to get a database session. FastAPI will call this function when it needs a database session. Only one thread at a time.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
