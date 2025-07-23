from unittest.mock import MagicMock, patch

import pytest
from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from books_collection.account.enums import State
from books_collection.account.models import Account
from books_collection.account.schemas import (
    AccountResponse,
    AccountUpdate,
    FilterAccount,
)
from books_collection.account.service import (
    create_account,
    delete_account,
    list_accounts,
    update_account,
)
from books_collection.common.exception.errors import (
    DuplicatedRegistry,
    ForbidenOperation,
)
from tests.account.factories import AccountFactory, AccountRequestFactory


@pytest.mark.asyncio
async def test_create_account_successfully(mock_session):
    request = AccountRequestFactory.create(password='123@123ddd')
    hashed_password = 'hashed_pass_4321'

    def refresh_side_effect(account_obj):
        account_obj.id = 1

    mock_session.refresh.side_effect = refresh_side_effect

    with patch(
        'books_collection.account.service.hash_password',
        return_value=hashed_password,
    ) as mock_hash_password:
        created_account = await create_account(request, mock_session)

    mock_hash_password.assert_called_once_with('123@123ddd')
    mock_session.add.assert_called_once()
    added_account = mock_session.add.call_args[0][0]
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(added_account)

    assert isinstance(added_account, Account)
    assert created_account.id == 1
    assert created_account.username == request.username
    assert created_account.email == request.email
    assert created_account.state == State.enabled
    assert isinstance(created_account, AccountResponse)


@pytest.mark.asyncio
async def test_create_account_with_in_use_username(mock_session):
    request = AccountRequestFactory.create()
    exc_msg = f'username: {request.username} already in use'
    unique_exc = UniqueViolation('accounts_username_key')
    mock_session.commit.side_effect = IntegrityError(
        statement='statment', params=['any'], orig=unique_exc
    )

    with pytest.raises(DuplicatedRegistry, match=exc_msg):
        await create_account(request, mock_session)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_not_awaited()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_account_with_in_use_email(mock_session):
    request = AccountRequestFactory.create()
    exc_msg = f'email: {request.email} already in use'
    unique_exc = UniqueViolation('accounts_email_key')
    mock_session.commit.side_effect = IntegrityError(
        statement='statment', params=['any'], orig=unique_exc
    )

    with pytest.raises(DuplicatedRegistry, match=exc_msg):
        await create_account(request, mock_session)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_not_awaited()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_account_with_generic_unique_constraint(mock_session):
    request = AccountRequestFactory.create()
    exc_msg = 'username or email already in use'
    mock_session.commit.side_effect = IntegrityError(
        statement='statment', params=['any'], orig=UniqueViolation('anything')
    )

    with pytest.raises(DuplicatedRegistry, match=exc_msg):
        await create_account(request, mock_session)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_not_awaited()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_accounts_default_filters(mock_session):
    expected_size = 5
    accounts_list = AccountFactory.create_batch(size=expected_size)
    for i, account in enumerate(accounts_list):
        account.id = i + 1

    mock_scalar_result = MagicMock()
    mock_scalar_result.all.return_value = accounts_list
    mock_session.scalars.return_value = mock_scalar_result

    response = await list_accounts(FilterAccount(), mock_session)

    mock_session.scalars.assert_awaited_once()
    mock_session.scalars.return_value.all.assert_called_once()
    assert len(response.accounts) == expected_size
    assert response.accounts[0].id == accounts_list[0].id


@pytest.mark.asyncio
async def test_list_accounts_with_state_filter(mock_session):
    expected_size = 3
    query = FilterAccount(state=State.disabled)
    accounts_list = AccountFactory.create_batch(size=3, state=State.disabled)
    for i, account in enumerate(accounts_list):
        account.id = i + 1

    mock_scalar_result = MagicMock()
    mock_scalar_result.all.return_value = accounts_list
    mock_session.scalars.return_value = mock_scalar_result

    response = await list_accounts(query, mock_session)

    mock_session.scalars.assert_awaited_once()
    mock_session.scalars.return_value.all.assert_called_once()

    assert len(response.accounts) == expected_size
    assert response.accounts[0].state == accounts_list[0].state


@pytest.mark.asyncio
async def test_update_account_successfully(mock_session):
    new_email = 'fulano@email.com'
    account_to_update = AccountUpdate(email=new_email)
    db_account = AccountFactory.create()
    db_account.id = 1

    def refresh_side_effect(account_obj):
        account_obj.id = 1

    mock_session.refresh.side_effect = refresh_side_effect

    updated_account = await update_account(
        1, account_to_update, db_account, mock_session
    )

    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(db_account)

    assert updated_account.id == 1
    assert updated_account.email == new_email


@pytest.mark.asyncio
async def test_update_account_with_in_use_username(mock_session):
    new_username = 'fulano'
    expected_msg = f'username: {new_username} already in use'
    account_to_update = AccountUpdate(username=new_username)
    db_account = AccountFactory.create()
    db_account.id = 1
    unique_exc = UniqueViolation('accounts_username_key')
    mock_session.commit.side_effect = IntegrityError(
        statement='statment', params=['any'], orig=unique_exc
    )

    with pytest.raises(DuplicatedRegistry, match=expected_msg):
        await update_account(1, account_to_update, db_account, mock_session)

    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_not_awaited()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_account_with_in_use_email(mock_session):
    new_email = 'fulano@email.com'
    expected_msg = f'email: {new_email} already in use'
    account_to_update = AccountUpdate(email=new_email)
    db_account = AccountFactory.create()
    db_account.id = 1
    unique_exc = UniqueViolation('accounts_email_key')
    mock_session.commit.side_effect = IntegrityError(
        statement='statment', params=['any'], orig=unique_exc
    )

    with pytest.raises(DuplicatedRegistry, match=expected_msg):
        await update_account(1, account_to_update, db_account, mock_session)

    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_not_awaited()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_account_with_generic_unique_constraint(mock_session):
    new_email = 'fulano@email.com'
    exc_msg = 'username or email already in use'
    account_to_update = AccountUpdate(email=new_email)
    db_account = AccountFactory.create()
    db_account.id = 1
    mock_session.commit.side_effect = IntegrityError(
        statement='statment', params=['any'], orig=UniqueViolation('anything')
    )

    with pytest.raises(DuplicatedRegistry, match=exc_msg):
        await update_account(1, account_to_update, db_account, mock_session)

    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_not_awaited()
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_account_not_enough_permission(mock_session):
    exc_msg = 'not enough permissions to update account'
    account_to_update = AccountUpdate()
    db_account = AccountFactory.create()
    db_account.id = 1
    with pytest.raises(ForbidenOperation, match=exc_msg):
        await update_account(11, account_to_update, db_account, mock_session)

    mock_session.commit.assert_not_awaited()
    mock_session.refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_account_successfully(mock_session):
    db_account = AccountFactory.create()
    db_account.id = 1
    await delete_account(1, db_account, mock_session)

    mock_session.delete.assert_awaited_once_with(db_account)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_account_not_enough_permission(mock_session):
    exc_msg = 'not enough permissions to delete account'
    db_account = AccountFactory.create()
    db_account.id = 1
    with pytest.raises(ForbidenOperation, match=exc_msg):
        await delete_account(21, db_account, mock_session)

    mock_session.delete.assert_not_awaited()
    mock_session.commit.assert_not_awaited()
