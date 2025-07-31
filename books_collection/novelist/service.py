from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from books_collection.common.exception.errors import (
    DuplicatedRegistry,
    RegistryNotFound,
)
from books_collection.novelist.models import Novelist
from books_collection.novelist.schemas import (
    FilterNovelist,
    NovelistList,
    NovelistRequest,
    NovelistResponse,
    NovelistUpdate,
)


async def create_novelist(
    novelist: NovelistRequest, session: AsyncSession
) -> NovelistResponse:
    new_novelist = Novelist(name=novelist.name)

    try:
        session.add(new_novelist)
        await session.commit()
        await session.refresh(new_novelist)

        return NovelistResponse(**asdict(new_novelist))
    except IntegrityError as ex:
        await session.rollback()

        error_detail = ex.orig
        if 'novelists_name_key' in error_detail:
            raise DuplicatedRegistry(
                f'name: {novelist.name} is already in use'
            )
        raise DuplicatedRegistry('duplicated registry error')


async def list_novelists(
    filter: FilterNovelist, session: AsyncSession
) -> NovelistList:
    query = select(Novelist).offset(filter.offset).limit(filter.limit)

    if filter.name:
        query = query.filter(filter.name in Novelist.name)

    result = await session.scalars(query)
    novelists = result.all()

    return NovelistList(novelists=novelists)


async def update_novelist(
    id: int, novelist_update: NovelistUpdate, session: AsyncSession
) -> NovelistResponse:
    novelist = get_novelist_or_raise(id, session)
    for key, value in novelist_update.model_dump(exclude_unset=True).items():
        setattr(novelist, key, value)

    await session.commit()
    await session.refresh(novelist)

    return NovelistResponse(**asdict(novelist))


async def delete_novelist(id: int, session: AsyncSession) -> None:
    novelist = get_novelist_or_raise(id, session)
    await session.delete(novelist)
    await session.commit()


async def get_novelist_or_raise(id: int, session: AsyncSession) -> Novelist:
    novelist = await session.scalar(select(Novelist).where(Novelist.id == id))
    if novelist:
        return novelist

    raise RegistryNotFound('novelist not found')
