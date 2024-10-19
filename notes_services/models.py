# Importing required liberaries and modules and settings

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text, Integer, ForeignKey, Table 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from settings import settings
from sqlalchemy.dialects.postgresql import JSONB


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
        
# Creating association table to form many to many relationship between notes and lables table
association_table = Table(
    'mid', 
    Base.metadata,
    Column('note_id', ForeignKey('notes.id'), primary_key=True),
    Column('label_id', ForeignKey('labels.id'), primary_key = True)
)

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
    collaborators = Column(JSONB, default = dict) #JSONB  field to store the collaborators

    # Creating relationship between lables and notes for access of each other
    labels = relationship("Labels", secondary=association_table, back_populates='notes')

    # Modification in t0_dict method for getting notes as well as labesl associated with it
    @property
    def to_dict(self):
        object_data = {col.name: getattr(self, col.name) for col in self.__table__.columns}
        labels = []
        if self.labels:
            labels = [x.to_dict for x in self.labels]
        object_data.update(labels = labels) #Updating object_data with labels and return it
        object_data.update(collaborators = self.collaborators) #Updating objext_data collaborators and return it
        return object_data
    
class Labels(Base):
    __tablename__ = "labels"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    color = Column(String, nullable=True)
    user_id = Column(BigInteger, index=True, nullable=False)
    
    # Creating relationship between lables and notes for access of each other
    notes = relationship("Notes", secondary=association_table, back_populates='labels')

    # Gives the labesl in dict format
    @property
    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

