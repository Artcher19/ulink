from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from schemas.links import LinkAddSchema
from api.dependencies import SessionDep
from database import setup_database
from models.links import LinkModel
from datetime import datetime
from api.service import calculate_control_digit, get_next_link_id
from config_reader import config
router = APIRouter()

@router.post('/links', summary='Создать сокращенную ссылку', description='Возвращает сокращенную ссылку', tags = ['links'])
async def create_short_link(data: LinkAddSchema, session: SessionDep):
    new_link_id = await get_next_link_id(session)
    control_digit = await calculate_control_digit(new_link_id)
    short_link = str(new_link_id) + str(control_digit)
    full_short_link = f'{config.protocol}://{config.domain}/{short_link}'
    new_link = LinkModel(
        link_id = new_link_id,
        full_link = data.full_link,
        short_link = short_link,
        create_date = datetime.now()
    )
    session.add(new_link)
    await session.commit()
    return {'short_link': full_short_link }

@router.get('/{short_link}', summary = 'Переадресовать пользователя', tags = ['links'])
async def redirect_user(short_link: str, session: SessionDep):
    query = select(LinkModel).where(LinkModel.short_link == short_link)
    result = await session.execute(query)
    link = result.scalar_one_or_none()
    
    if link is None:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    
    # Осуществляем редирект на полную ссылку
    return RedirectResponse(url=link.full_link)


@router.post('/setup_sqlite', summary = 'Создать структуру БД', tags = ['tech'])
async def create_db():
    await setup_database()
    return 'database created'