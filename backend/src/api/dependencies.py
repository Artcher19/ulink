from typing import Annotated
from fastapi import Depends
import ydb
from ydbase import get_ydb_session
from database import get_session

#SessionDep = Annotated[AsyncSession, Depends(get_session)]
# YdbSessionDep = Annotated[ydb.aio.query.session.QuerySession, Depends(get_ydb_session)]


