import os
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from config_reader import config
from models.links import Base
from sqlalchemy import text

engine = create_async_engine(f"sqlite+aiosqlite:///{config.sqlite_database_path}")
new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with new_session() as session:
        yield session
        
async def database_exists():
    """Проверяет, существует ли база данных и содержит ли таблицы"""
    if not os.path.exists(config.sqlite_database_path):
        return False
    
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.fetchall()
            return len(tables) > 0
    except Exception:
        return False


async def setup_database():
    """Создать базу данных, если она не создана"""
    if await database_exists():
        raise Exception("База данных уже создана")
    
    async with engine.begin() as conn:
       await conn.run_sync(Base.metadata.drop_all)
       await conn.run_sync(Base.metadata.create_all)

async def reload_database_connection():
    """Перезагружает соединение с базой данных (после восстановления из backup)"""
    global engine, new_session
    # Создаем новое соединение
    engine = create_async_engine(f"sqlite+aiosqlite:///{config.sqlite_database_path}")
    new_session = async_sessionmaker(engine, expire_on_commit=False)