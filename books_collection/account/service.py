from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from books_collection.database.config import get_session

Session = Annotated[AsyncSession, Depends(get_session)]


async def do_something(session: Session):
    ...
