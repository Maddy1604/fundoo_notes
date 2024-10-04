# Importing required liberaries and modules and settings

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from settings import settings

# Defining base with declarative base
Base = declarative_base()

# creating engine object with create engine module and assigning database url which importing from settings
engine = create_engine(settings.notes_db_url)
# Creating local session for transaction using sessionmaker wiht parameter bind to start engine aand autocommit false
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

# Creating class with base parameter in that creating and assigning properties to columns
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

    @property
    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}
    
class Labels(Base):
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    color = Column(String, nullable=True)
    user_id = Column(BigInteger, index=True, nullable=False)

    