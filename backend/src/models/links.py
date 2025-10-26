from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, INT , VARCHAR, TIMESTAMP

class Base(DeclarativeBase):
    pass

class LinkModel(Base):
    __tablename__ = 'links'
    
    link_id = Column(INT, primary_key=True, autoincrement=True, nullable=False )
    full_link = Column(VARCHAR, nullable=False)
    short_link = Column(INT, index=True)
    create_date = Column(TIMESTAMP)