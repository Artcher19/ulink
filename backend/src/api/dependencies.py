import hashlib
import secrets
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from database import get_session
from sqlalchemy.ext.asyncio import  AsyncSession
from config_reader import config

SessionDep = Annotated[AsyncSession, Depends(get_session)]


# Настройки для базовой аутентификации
security = HTTPBasic()

# Функция для проверки базовой аутентификации
async def basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, config.admin_username)
    input_password_hash = hashlib.sha256(credentials.password.encode('utf-8')).hexdigest()
    correct_password = secrets.compare_digest(input_password_hash, config.admin_password_hash)  # Замените на реальный пароль
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username