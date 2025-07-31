from datetime import timedelta

import pytest
from fastapi.exceptions import HTTPException
from freezegun import freeze_time
from jwt import decode

from books_collection.auth.security import (
    create_access_token,
    get_current_account,
    hash_password,
    verify_password,
)
from books_collection.settings import settings


def test_hash_password():
    plain_pass = '123456@asdfgh'
    hashed_pass = hash_password(plain_pass)

    assert plain_pass != hashed_pass
    assert verify_password(plain_pass, hashed_pass)


def test_create_token():
    email = 'xx@email.com'
    token, _ = create_access_token(data={'sub': email})

    decoded_token = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert 'sub' in decoded_token
    assert 'exp' in decoded_token
    assert decoded_token.get('sub') == email


def test_create_token_valid_expiration_time():
    token, expires_in = create_access_token(data={'sub': 'email'})

    decoded_token = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert 'exp' in decoded_token
    assert decoded_token.get('exp') == expires_in


@pytest.mark.asyncio
async def test_get_current_account(session, account):
    token, _ = create_access_token(data={'sub': account.email})
    db_account = await get_current_account(session, token)

    assert db_account.id == account.id
    assert db_account.email == account.email


@pytest.mark.asyncio
async def test_get_current_account_malformed_token(session):
    with pytest.raises(HTTPException, match='Could not validate credentials'):
        await get_current_account(session, 'token')


@pytest.mark.asyncio
async def test_get_current_account_without_valid_token_sub(session):
    token, _ = create_access_token(data={'test': 'asd'})
    with pytest.raises(HTTPException, match='Could not validate credentials'):
        await get_current_account(session, token)


@pytest.mark.asyncio
async def test_get_current_account_with_expired_token(session, account):
    exc_msg = 'Could not validate credentials'
    with freeze_time('2025-07-10 12:00:00') as frozen_time:
        token, _ = create_access_token(data={'sub': account.email})

        frozen_time.tick(timedelta(seconds=301))

        with pytest.raises(HTTPException, match=exc_msg):
            await get_current_account(session, token)


@pytest.mark.asyncio
async def test_get_current_account_with_not_found_account(session):
    token, _ = create_access_token(data={'sub': 'another_email@mail.com'})
    with pytest.raises(HTTPException, match='Could not validate credentials'):
        await get_current_account(session, token)
