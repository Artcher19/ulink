from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from api.utils import calculate_control_digit
from schemas.links import LinkAddSchema
from config_reader import config
from api import crud
from ydbase import ydb_connection
from api.dependencies import SessionDep


async def create_short_link(data: LinkAddSchema, session: SessionDep):
    """Создать коротку ссылку"""
    link_id = await crud.post_link(data.full_link, session)
    new_link_id = 10000 + link_id
    control_digit = await calculate_control_digit(new_link_id)
    short_link = str(new_link_id) + str(control_digit)   
    await crud.update_link(link_id, short_link, session)
    full_short_link = f'{config.public_domain}/{short_link}'
    return {"short_link": full_short_link}

async def redirect_user(short_link: str, session: SessionDep): # type: ignore
    """Осуществить редирект пользователя"""
    full_link = await crud.get_full_link_by_short_link(short_link, session)
    if full_link is None:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")
    return RedirectResponse(url=full_link)