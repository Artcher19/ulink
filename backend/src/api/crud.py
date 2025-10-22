from ydbase import ydb_connection

async def get_full_link_by_short_link(short_link: str, session):
    query = """
    SELECT full_link FROM links WHERE short_link = $short_link;
    """
    params = {'$short_link': short_link}

    # async with ydb_connection.get_session() as session:
    #     result_set = await session.execute(  
    #         query,
    #         params
    #     )
    result_set = await session.execute(  
            query,
            params
        )
    full_link = None
    async for result in result_set:
        if result and result.rows:
            full_link = result.rows[0].full_link
            break
    return full_link


async def post_link( full_link: str, session):
    # YQL запрос для вставки данных с преобразованием в Timestamp
    query = """
        UPSERT INTO links (full_link, create_date)
        VALUES ($full_link, CurrentUtcTimestamp())
        RETURNING link_id;
        """
    
    # Параметры для запроса - передаем время в формате для Timestamp
    params = {
        '$full_link': full_link
    }
        
    # async with ydb_connection.get_session() as session:
        
    #     result_set = await session.transaction().execute(
    #         query,
    #         params,
    #         True
    #     )

    #     async for result in result_set:
    #         if result and result.rows:
    #             link_id = result.rows[0].link_id
    #             break
    result_set = await session.transaction().execute(
            query,
            params,
            True
        )

    async for result in result_set:
            if result and result.rows:
                link_id = result.rows[0].link_id
                break
    
    return link_id

async def update_link(link_id: int, short_link: str, full_link: str, session):
    query = """
        UPSERT INTO links (link_id, short_link, full_link, create_date)
        VALUES ($link_id, $short_link, $full_link, CurrentUtcTimestamp());
    """

    params = {
        '$link_id': link_id,
        '$short_link': short_link,
        '$full_link': full_link
    }

    # async with ydb_connection.get_session() as session:
    #     await session.transaction().execute(
    #         query,
    #         params,
    #         True
    #     )

    await session.transaction().execute(
            query,
            params,
            True
        )


