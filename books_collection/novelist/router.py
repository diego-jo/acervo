from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from books_collection.auth.security import get_current_account
from books_collection.common.dependencies import Session
from books_collection.novelist.schemas import (
    FilterNovelist,
    NovelistList,
    NovelistRequest,
    NovelistResponse,
    NovelistUpdate,
)
from books_collection.novelist.service import (
    create_novelist,
    delete_novelist,
    list_novelists,
    update_novelist,
)

router = APIRouter(
    prefix='/novelists',
    tags=['novelists'],
    dependencies=[Depends(get_current_account)],
)

QueryParam = Annotated[FilterNovelist, Query()]


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=NovelistResponse
)
async def create(novelist: NovelistRequest, session: Session):
    return await create_novelist(novelist, session)


@router.get('/', status_code=HTTPStatus.OK, response_model=NovelistList)
async def list(filters: QueryParam, session: Session):
    return await list_novelists(filters, session)


@router.patch(
    '/{id}', status_code=HTTPStatus.OK, response_model=NovelistResponse
)
async def update(id: int, novelist: NovelistUpdate, session: Session):
    return await update_novelist(id, novelist)


@router.delete('/{id}', status_code=HTTPStatus.NO_CONTENT)
async def delete(id: int, session: Session):
    await delete_novelist(id, session)
