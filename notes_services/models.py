from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from settings import settings

Base = declarative_base()

engine = create_engine(settings.notes_db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

class Notes(Base):
    __tablename__ = "notes"
    
    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    color = Column(String, nullable=True)
    is_archive = Column(Boolean, default=False, index=True)
    is_trash = Column(Boolean, default=False, index=True)
    reminder = Column(DateTime, nullable=True)
    user_id = Column(BigInteger, nullable=False, index=True)

    