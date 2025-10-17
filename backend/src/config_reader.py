from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os


class Settings(BaseSettings):
    domain: str = Field(default='localhost:8000')
    protocol: str = Field(default='http')
    ydb_endpoint: str = Field(default = 'grpcs://ydb.example.com:2135')
    ydb_database: str = Field(default= '/ru-central1/yihg94cbcei3ghew/gh4gcuv494v')
    ydb_pool_size: int = Field(default = 50)

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), '..', '.env'),
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

config = Settings()
