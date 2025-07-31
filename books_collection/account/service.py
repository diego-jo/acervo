from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from books_collection.account.models import Account
from books_collection.account.schemas import (
    AccountRequest,
    AccountResponse,
    AccountsList,
    AccountUpdate,
    FilterAccount,
)
from books_collection.auth.security import hash_password
from books_collection.common.exception.errors import (
    DuplicatedRegistry,
    ForbidenOperation,
)


async def create_account(
    account: AccountRequest, session: AsyncSession
) -> AccountResponse:
    new_account = Account(
        username=account.username,
        email=account.email,
        password=hash_password(account.password),
    )
    try:

        session.add(new_account)
        await session.commit()
        await session.refresh(new_account)

        return AccountResponse(**asdict(new_account))
    except IntegrityError as ex:
        await session.rollback()

        error_detail = str(ex.orig)
        if 'accounts_username_key' in error_detail:
            exc_msg = f'username: {account.username} is already in use'
            raise DuplicatedRegistry(exc_msg)

        if 'accounts_email_key' in error_detail:
            exc_msg = f'email: {account.email} is already in use'
            raise DuplicatedRegistry(exc_msg)

        raise DuplicatedRegistry('username or email is already in use')


# TODO: renomear query para filter chatão!
async def list_accounts(
    query: FilterAccount, session: AsyncSession
) -> AccountsList:
    sql_query = select(Account).offset(query.offset).limit(query.limit)

    if query.state:
        sql_query = sql_query.filter(Account.state == query.state)

    result = await session.scalars(sql_query)

    accounts = result.all()

    return AccountsList(accounts=accounts)


async def update_account(
    id: int,
    account_update: AccountUpdate,
    account: Account,
    session: AsyncSession,
) -> AccountResponse:
    # TODO: pode ser extraído para uma dependência em cadeia!
    if account.id != id:
        raise ForbidenOperation('not enough permissions to update account')

    for key, value in account_update.model_dump(exclude_unset=True).items():
        setattr(account, key, value)

    try:
        await session.commit()
        await session.refresh(account)

        return AccountResponse(**asdict(account))
    except IntegrityError as ex:
        await session.rollback()

        error_detail = str(ex.orig)
        if 'accounts_username_key' in error_detail:
            exc_msg = f'username: {account_update.username} is already in use'
            raise DuplicatedRegistry(exc_msg)

        if 'accounts_email_key' in error_detail:
            exc_msg = f'email: {account_update.email} is already in use'
            raise DuplicatedRegistry(exc_msg)

        raise DuplicatedRegistry('username or email is already in use')


async def delete_account(
    id: int, account: Account, session: AsyncSession
) -> None:
    if account.id != id:
        raise ForbidenOperation('not enough permissions to delete account')
    await session.delete(account)
    await session.commit()
