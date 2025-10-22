from fastapi import Depends
from datetime import datetime
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import func, select, text
from config_reader import config

engine = create_async_engine(f"postgresql+asyncpg://{config.pg_username}:{config.pg_username}@{config.pg_host}/{config.pg_database_name}")
new_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_session():
    async with new_session() as session:
        yield session
        