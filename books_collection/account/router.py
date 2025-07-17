from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from books_collection.account.models import Account
from books_collection.account.schemas import (
    AccountRequest,
    AccountResponse,
    AccountsList,
    AccountUpdate,
    FilterAccount,
)
from books_collection.account.service import (
    create_account,
    delete_account,
    list_accounts,
    update_account,
)
from books_collection.auth.security import get_current_account
from books_collection.common.dependencies import Session

router = APIRouter(prefix='/accounts', tags=['accounts'])
CurrentAccount = Annotated[Account, Depends(get_current_account)]
QueryParam = Annotated[FilterAccount, Query()]


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=AccountResponse
)
async def create(account: AccountRequest, session: Session):
    return await create_account(account, session)


@router.get('/', status_code=HTTPStatus.OK, response_model=AccountsList)
async def list(filters: QueryParam, session: Session):
    return await list_accounts(filters, session)


@router.patch(
    '/{id}', status_code=HTTPStatus.OK, response_model=AccountResponse
)
async def update(
    id: int,
    account_update: AccountUpdate,
    account: CurrentAccount,
    session: Session,
):
    return await update_account(id, account_update, account, session)


@router.delete('/{id}', status_code=HTTPStatus.NO_CONTENT)
async def delete(id: int, account: CurrentAccount, session: Session):
    await delete_account(id, account, session)
