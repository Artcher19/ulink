from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from schemas.links import LinkAddSchema
from api.dependencies import SessionDep
from database import setup_database
from api.service import create_short_link, redirect_user
from config_reader import config
router = APIRouter()

@router.post('/links', summary='Создать сокращенную ссылку', description='Возвращает сокращенную ссылку', tags = ['links'])
async def post_link(data: LinkAddSchema, session: SessionDep):
    return await create_short_link(data, session)

@router.get('/{short_link}', summary = 'Переадресовать пользователя', tags = ['links'])
async def get_full_link(short_link: str, session: SessionDep):
    return await redirect_user(short_link, session)


@router.post('/setup_sqlite', summary = 'Создать структуру БД', tags = ['tech'])
async def create_db():
    await setup_database()
    return 'database created'