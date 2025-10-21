# from fastapi import Depends
# from datetime import datetime
# from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
# from sqlalchemy.orm import DeclarativeBase
# from sqlalchemy import func, select, text


# db_filename= "database.db"
# engine = create_async_engine(f"sqlite+aiosqlite:///{db_filename}")
# new_session = async_sessionmaker(engine, expire_on_commit=False)

# class Base(DeclarativeBase):
#     pass

# async def setup_database():
#     async with engine.begin() as conn:
#        await conn.run_sync(Base.metadata.drop_all)
#        await conn.run_sync(Base.metadata.create_all)

# async def get_session():
#     async with new_session() as session:
#         yield session
        