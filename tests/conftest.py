import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from books_collection.account.models import Account
from books_collection.app import app
from books_collection.auth.security import hash_password
from books_collection.database.config import get_session
from books_collection.database.tables import table_registry


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer(image='postgres:16', driver='psycopg') as postgres:
        _engine = create_async_engine(postgres.get_connection_url())
        yield _engine


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def account(session):
    plain_password = '123@asd'

    new_account = Account(
        username='diego',
        email='diego@email.com',
        password=hash_password(plain_password)
    )

    session.add(new_account)
    await session.commit()
    await session.refresh(new_account)

    new_account.plain_password = plain_password

    return new_account


@pytest.fixture
def client(session):
    def override_session():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = override_session
        yield client
        app.dependency_overrides.clear()
