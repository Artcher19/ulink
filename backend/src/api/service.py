from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from api.dependencies import SessionDep
from api.utils import calculate_control_digit
from schemas.links import LinkAddSchema
from models.links import LinkModel
from config_reader import config

async def get_next_link_id(session: SessionDep) -> int:
    """Получить следующий ID для ссылки, начиная с 10000"""
    result = await session.execute(select(func.max(LinkModel.link_id)))
    max_id = result.scalar()
    
    if max_id is None:
        return 10000
    else:
        return max_id + 1

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

async def redirect_user(short_link: str, session: SessionDep):
    query = select(LinkModel).where(LinkModel.short_link == short_link)
    result = await session.execute(query)
    link = result.scalar_one_or_none()
    
    if link is None:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    
    return RedirectResponse(url=link.full_link)