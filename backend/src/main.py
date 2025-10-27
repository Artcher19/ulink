from fastapi import FastAPI
import uvicorn
from api import base_router
from logging_middleware import LoggingMiddleware
from config_reader import config




app = FastAPI(
    title='ShortLinkApp',
    description='Сервис для сокращения ссылок',
    version = 'v1.2.0',
    redoc_url=None,
)

app.add_middleware(LoggingMiddleware)

app.include_router(base_router)


if __name__ == "__main__":
    uvicorn.run('main:app', host = '0.0.0.0', port = int(config.uvicorn_port), reload=True)