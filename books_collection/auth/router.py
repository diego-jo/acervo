from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from books_collection.account.models import Account
from books_collection.auth.schemas import Token
from books_collection.auth.security import verify_password
from books_collection.database.config import get_session

router = APIRouter(prefix='/auth', tags=['auth'])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
Session = Annotated[AsyncSession, Depends(get_session)]


@router.post('/token', status_code=HTTPStatus.OK, response_model=Token)
async def login(form_data: OAuth2Form, session: Session):
    db_account = await session.scalar(
        select(Account).where(Account.email == form_data.username)
    )

    if not db_account or not verify_password(
        form_data.password, db_account.password
    ):
        raise ''
