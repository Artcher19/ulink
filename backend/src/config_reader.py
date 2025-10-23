from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Literal
import os


class Settings(BaseSettings):
    public_domain: str = Field(default='localhost:8080', description="Публичный домен сокращенной ссылки для отображения пользователю")
    ydb_endpoint: str = Field(default = 'grpcs://ydb.example.com:2135')
    ydb_database: str = Field(default= '/ru-central1/<ваше значение из YDB>/<ваше значение из YDB>')
    ydb_pool_size: int = Field(default = 1000)
    authorized_key_base64: str = Field(default = '', description='Base64 значение json конфига сервисного аккаунта для управления YDB')
    uvicorn_port: str = Field(default='8080')
    pg_username: str = Field(default='user')
    pg_password: str = Field(default = 'password')
    pg_host: str = Field(default = 'localhost:5432')
    pg_database_name: str = Field(default = 'database')
    ca_path: str = Field(default = "links/backend/certs/RootCA.pem")
    deploy_zone: Literal['dev', 'prod'] = Field(default='dev')
    sqlite_database: str = Field(default = "database.db")


    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), '..', '.env'),
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

config = Settings()

