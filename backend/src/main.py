from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from api import base_router
from config_reader import config
from fastapi.middleware.cors import CORSMiddleware
from ydbase import ydb_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация при запуске
    # await setup_database()
    await ydb_connection.initialize()
    yield
    # Очистка при завершении
    await ydb_connection.close()
    
app = FastAPI(lifespan=lifespan)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[f"{config.protocol}://{config.domain}:8080"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(base_router)


if __name__ == "__main__":
    uvicorn.run('main:app', host = '0.0.0.0', reload=True)