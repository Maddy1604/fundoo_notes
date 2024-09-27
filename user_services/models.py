from sqlalchemy import Integer, Column, String, Boolean, DateTime, func, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from settings import settings

engine = create_engine(url=settings.db_url)

session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


    @property
    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns if col.name != "password"}


