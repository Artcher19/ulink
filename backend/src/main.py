from fastapi import FastAPI
import uvicorn
from api import base_router
from config_reader import config
from fastapi.middleware.cors import CORSMiddleware

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await ydb_connection.initialize()
#     yield
#     await ydb_connection.close()

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[f"{config.protocol}://{config.domain}:8080"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(base_router)


if __name__ == "__main__":
    uvicorn.run('main:app', host = '0.0.0.0', port = int(config.uvicorn_port), reload=True)