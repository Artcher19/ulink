from typing import Annotated
from sqlalchemy.ext.asyncio import  AsyncSession
from fastapi import Depends
import ydb
from ydbase import get_ydb_session
from database import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
YdbSessionDep = Annotated[object, Depends(get_ydb_session)]


