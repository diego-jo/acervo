from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from books_collection.account.models import Account
from books_collection.auth.schemas import Token
from books_collection.auth.security import (
    create_access_token,
    get_current_account,
    verify_password,
)
from books_collection.common.dependencies import Session

router = APIRouter(prefix='/auth', tags=['auth'])

CurrentAccount = Annotated[Account, Depends(get_current_account)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', status_code=HTTPStatus.OK, response_model=Token)
async def login(form_data: OAuth2Form, session: Session):
    db_account = await session.scalar(
        select(Account).where(Account.email == form_data.username)
    )

    if not db_account or not verify_password(
        form_data.password, db_account.password
    ):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='invalid username or password',
        )

    token, expires_in = create_access_token({'sub': form_data.username})

    return Token(access_token=token, expires_in=expires_in)


@router.post('/refresh_token', status_code=HTTPStatus.OK, response_model=Token)
def refresh_token(account: CurrentAccount):
    token, expires_in = create_access_token({'sub': account.email})

    return Token(access_token=token, expires_in=expires_in)
