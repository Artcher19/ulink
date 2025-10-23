import asyncio
import ssl
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from config_reader import config
from models.links import Base

engine = create_async_engine(f"sqlite+aiosqlite:///{config.sqlite_database}")

if config.deploy_zone == 'dev':
    # Создаем SSL контекст с CA-сертификатом
    ssl_context = ssl.create_default_context(cafile=config.ca_path)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_REQUIRED

    ssl_args = {'ssl': ssl_context}
    engine = create_async_engine(f"postgresql+asyncpg://{config.pg_username}:{config.pg_password}@{config.pg_host}/{config.pg_database_name}",
                                connect_args=ssl_args)
else:
    engine = create_async_engine(f"postgresql+asyncpg://{config.pg_username}:{config.pg_password}@{config.pg_host}/{config.pg_database_name}")
    
new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with new_session() as session:
        yield session
        

# async def setup_database():
#     async with engine.begin() as conn:
#        await conn.run_sync(Base.metadata.drop_all)
#        await conn.run_sync(Base.metadata.create_all)

# asyncio.run(setup_database())