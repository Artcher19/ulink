from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from schemas.links import LinkAddSchema
from api.dependencies import SessionDep, YdbSessionDep
from database import setup_database
from api.service import create_short_link, redirect_user
from config_reader import config

router = APIRouter(tags=['links'])

@router.post('/links', summary='Создать сокращенную ссылку', description='Возвращает сокращенную ссылку')
async def post_link(data: LinkAddSchema, session: YdbSessionDep):
    return await create_short_link(data, session)

@router.get('/{short_link}', summary = 'Переадресовать пользователя')
async def get_full_link(short_link: str, session: YdbSessionDep):
    return await redirect_user(short_link, session)


# @router.post('/setup_sqlite', summary = 'Создать структуру БД', tags = ['tech'])
# async def create_db():
#     await setup_database()
#     return 'database created'