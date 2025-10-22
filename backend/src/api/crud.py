from api.dependencies import SessionDep
from models.links import LinkModel
from sqlalchemy import select, insert, update
from datetime import datetime

async def get_full_link_by_short_link(short_link: str, session: SessionDep):
    query = select(LinkModel.full_link).where(LinkModel.short_link == short_link)
    result = await session.execute(query)
    link = result.scalar_one_or_none()
    return link

async def post_link( full_link: str, session: SessionDep):
    stmt = (
        insert(LinkModel)
        .values(full_link=full_link)
        .returning(LinkModel.link_id)
    )
    result = await session.execute(stmt)
    link_id = result.scalar_one()
    await session.commit()
    return link_id

async def update_link(link_id: int, short_link: str, session: SessionDep):
    stmt = (
        update(LinkModel)
        .where(LinkModel.link_id == link_id)
        .values(short_link=short_link, create_date=datetime.now())
    )
    await session.execute(stmt)
    await session.commit()


