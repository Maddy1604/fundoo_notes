from sqlalchemy import Integer, BigInteger, String, Column, Boolean, create_engine, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from settings import settings

engine = create_engine(url=settings.notes_db_url)

session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


class Notes(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    color = Column(String, nullable=True)
    is_archive = Column(Boolean, index=True, default=False)
    is_trash = Column(Boolean, index=True, default=False)
    reminder = Column(DateTime, nullable=True)
    user_id = Column(BigInteger, index=True, nullable=False)

    @property
    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns if col.name != "password"}