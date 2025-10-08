from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func, select, text
from datetime import datetime
from database import Base

class LinkModel(Base):
    __tablename__ = 'links'
    
    link_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_link: Mapped[str]
    short_link: Mapped[str]
    create_date: Mapped[datetime]