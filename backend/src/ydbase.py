import os
import ydb
from config_reader import config
from contextlib import asynccontextmanager

key_path = os.path.join(os.path.dirname(__file__), '..', 'authorized_key.json')

class YDBConnection:
    def __init__(self):
        self.driver = None
        self.pool = None
    
    async def initialize(self):
        """Инициализация драйвера и пула"""
        self.driver = ydb.aio.Driver(
            endpoint=config.ydb_endpoint,
            database=config.ydb_database,
            credentials=ydb.iam.ServiceAccountCredentials.from_file(key_file=key_path)
        )
        await self.driver.wait(timeout=5, fail_fast=True)
        self.pool = ydb.aio.QuerySessionPool(self.driver)
    
    async def close(self):
        """Закрытие соединений"""
        if self.pool:
            await self.pool.stop()
        if self.driver:
            await self.driver.stop()
    
    @asynccontextmanager
    async def get_session(self):
        """Контекстный менеджер для получения сессии"""
        if not self.pool:
            await self.initialize()
        
        async with self.pool.async_session() as session:
            yield session

# Создаем экземпляр для использования в приложении
ydb_connection = YDBConnection()

async def get_ydb_session():
    """Зависимость для FastAPI"""
    async with ydb_connection.get_session() as session:
        yield session