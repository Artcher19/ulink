import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from config_reader import config
from models.links import Base

engine = create_async_engine(f"sqlite+aiosqlite:///{config.sqlite_database}")
new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with new_session() as session:
        yield session
        

# async def setup_database():
#     async with engine.begin() as conn:
#        await conn.run_sync(Base.metadata.drop_all)
#        await conn.run_sync(Base.metadata.create_all)

# asyncio.run(setup_database())