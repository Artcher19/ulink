from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Literal
import os


class Settings(BaseSettings):
    public_domain: str = Field(default='localhost:8080', description="Публичный домен сокращенной ссылки для отображения пользователю")
    uvicorn_port: str = Field(default='8080')
    sqlite_database_path: str = Field(default = "database.db")
    admin_username: str = Field(default='admin')
    admin_password_hash: str = Field(default='5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8')
    aws_access_key_id: str = Field(default="")
    aws_secret_access_key: str = Field(default="")
    endpoint_url: str = Field(default="https://storage.yandexcloud.net")

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), '..', '.env'),
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

config = Settings()

