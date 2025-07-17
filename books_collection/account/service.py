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
    # TODO: entender pq mesmo com retorno de erro pelo pydantic no controller
    # o id do banco é incrementado sem inserção
    new_account = Account(
        username=account.username,
        email=account.email,
        password=hash_password(account.password),
    )

    try:
        session.add(new_account)
        await session.commit()
        await session.refresh(new_account)

        return new_account
    except IntegrityError as ex:
        msg = (
            ex.args[0]
            .split('DETAIL:')[1]
            .strip()
            .split(' ')[1]
            .replace('(', '')
            .replace(')', '')
            .split('=')
        )

        await session.rollback()
        raise DuplicatedRegistry(f'{msg[0]}: {msg[1]} already in use')


async def list_accounts(
    query: FilterAccount, db_session: AsyncSession
) -> AccountsList:
    sql_query = select(Account).offset(query.offset).limit(query.limit)

    if query.state:
        sql_query = sql_query.filter(Account.state == query.state)

    result = await db_session.scalars(sql_query)

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

        return account
    except IntegrityError as ex:
        msg = (
            ex.args[0]
            .split('DETAIL:')[1]
            .strip()
            .split(' ')[1]
            .replace('(', '')
            .replace(')', '')
            .split('=')
        )

        await session.rollback()
        raise DuplicatedRegistry(f'{msg[0]}: {msg[1]} already in use')


async def delete_account(
    id: int, account: Account, session: AsyncSession
) -> None:
    if account.id != id:
        raise ForbidenOperation('not enough permissions to delete account')
    await session.delete(account)
    await session.commit()
