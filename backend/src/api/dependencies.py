from typing import Annotated
from fastapi import Depends
from database import get_session
from sqlalchemy.ext.asyncio import  AsyncSession

SessionDep = Annotated[AsyncSession, Depends(get_session)]
# YdbSessionDep = Annotated[ydb.aio.query.session.QuerySession, Depends(get_ydb_session)]


