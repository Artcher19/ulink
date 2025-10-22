from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import BIGINT, TIMESTAMP
from datetime import datetime
from database import Base

class LinkModel(Base):
    __tablename__ = 'links'
    
    link_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    full_link: Mapped[str] = mapped_column(nullable=False)
    short_link: Mapped[str]
    create_date: Mapped[TIMESTAMP]