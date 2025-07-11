from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from books_collection.account.models import Account
from books_collection.database.config import get_session
from books_collection.settings import settings

context = PasswordHash.recommended()

oauth2_schema = OAuth2PasswordBearer(
    tokenUrl='/auth/token', refreshUrl='/auth/refresh_token'
)
Session = Annotated[AsyncSession, Depends(get_session)]


def hash_password(plain_password: str):
    return context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str):
    return context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expires_in = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        seconds=settings.TOKEN_TIME_EXPIRATION_SECS
    )
    to_encode.update({'exp': expires_in})

    token = encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)

    return token, int(expires_in.timestamp())


async def get_current_account(
    session: Session,
    token: str = Depends(oauth2_schema),
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authentication': 'Bearer'},
    )

    try:
        decoded_token = decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = decoded_token.get('sub')

        if not email:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    db_account = await session.scalar(
        select(Account).where(Account.email == email)
    )

    if not db_account:
        raise credentials_exception

    return db_account
