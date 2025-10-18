import base64
import json
import os
import ydb
from config_reader import config
from contextlib import asynccontextmanager


key_decoded_bytes = base64.b64decode(config.authorized_key_base64)
key_decoded_str = key_decoded_bytes.decode("utf-8")

class YDBConnection:
    def __init__(self):
        self.driver = None
        self.pool = None
    
    async def initialize(self):
        """Инициализация драйвера и пула"""
        self.driver = ydb.aio.Driver(
            endpoint=config.ydb_endpoint,
            database=config.ydb_database,
            credentials=ydb.iam.ServiceAccountCredentials.from_content(key=key_decoded_str)
        )
        await self.driver.wait(timeout=5, fail_fast=True)
        self.pool = ydb.aio.QuerySessionPool(self.driver, size = config.ydb_pool_size)
    
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
        
        # Используем acquire() для получения сессии из пула
        session = await self.pool.acquire() # type: ignore
        try:
            yield session
        finally:
            await self.pool.release(session) # type: ignore

# Создаем экземпляр для использования в приложении
ydb_connection = YDBConnection()

async def get_ydb_session():
    """Зависимость для FastAPI"""
    async with ydb_connection.get_session() as session:
        yield session