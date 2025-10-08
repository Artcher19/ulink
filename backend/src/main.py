from fastapi import FastAPI
import uvicorn
from api import base_router
from config_reader import config

app = FastAPI()
app.include_router(base_router)


if __name__ == "__main__":
    uvicorn.run('main:app', host = '0.0.0.0', reload=True)