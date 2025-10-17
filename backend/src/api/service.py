from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from api.dependencies import SessionDep, YdbSessionDep
from api.utils import calculate_control_digit
from schemas.links import LinkAddSchema
from models.links import LinkModel
from config_reader import config

async def get_next_link_id(session: YdbSessionDep) -> int:
    """Получить следующий ID для ссылки из БД, начиная с 10000"""
    
    query = """
        SELECT MAX(link_id) as max_id FROM links;
    """
    
    # Правильный способ выполнения запроса в YDB
    result_set = await session.execute(query)
    print(f"result_set: {result_set}")

    # Обрабатываем результат YDB
    async for result in result_set:
        print(f"result_rows: {result.rows}")
        if result and result.rows:
            max_id = result.rows[0].max_id
            break
    else:
        max_id = None
    
    if max_id is None:
        return 10000
    else:
        return max_id + 1

async def create_short_link(data: LinkAddSchema, session: YdbSessionDep):
    """Создать коротку ссылку"""
    new_link_id = await get_next_link_id(session)
    control_digit = await calculate_control_digit(new_link_id)
    short_link = str(new_link_id) + str(control_digit)
    full_short_link = f'{config.protocol}://{config.domain}/{short_link}'
    # YQL запрос для вставки данных
    query = """
        DECLARE $link_id AS Int
        DECLARE $full_link AS String 
        DECLARE $short_link AS String
        DECLARE $create_date AS Datetime

        UPSERT INTO links (link_id, full_link, short_link, create_date);
        """
    
    # Параметры для запроса
    params = {
        '$link_id': new_link_id,
        '$full_link': data.full_link,
        '$short_link': short_link,
        '$create_date': datetime.now().isoformat()
    }
    print(params)
    
    # Выполняем запрос через YDB сессию
    result = await session.execute(
        query,
        params
    )

    return {"short_link": full_short_link}

async def redirect_user(short_link: str, session: YdbSessionDep):
    """Осуществить редирект пользователя"""
    query = """
    SELECT full_link FROM links WHERE short_link = $short_link;
    """
    params = {'$short_link': short_link}

    # Правильный способ передачи параметров в YDB
    result_set = await session.execute(
        query,
        params
    )
    
    full_link = None
    async for result in result_set:
        if result and result.rows:
            full_link = result.rows[0].full_link  # Это уже строка с URL
            break
    
    if full_link is None:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")

    return RedirectResponse(url=full_link)