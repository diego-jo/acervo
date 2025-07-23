from http import HTTPStatus

import pytest

from books_collection.account.enums import State
from tests.account.factories import AccountFactory


def test_create_account_with_success(client):
    response = client.post(
        '/accounts',
        json={
            'username': 'diego',
            'email': 'diego@email.com',
            'password': '1234@asddfg',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'diego',
        'email': 'diego@email.com',
        'state': 'enabled',
    }


def test_create_account_with_missing_password(client):
    response = client.post(
        '/accounts', json={'username': 'json', 'email': 'email@email.com'}
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_create_account_with_missing_username(client):
    response = client.post(
        '/accounts',
        json={'password': '1234@asddfg', 'email': 'email@email.com'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_create_account_with_missing_email(client):
    response = client.post(
        '/accounts', json={'username': 'json', 'password': '1234@asddfg'}
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_create_account_with_invalid_password_length(client):
    response = client.post(
        '/accounts',
        json={
            'username': 'json',
            'email': 'email@email.com',
            'password': '1234@a',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_create_account_with_invalid_email(client):
    response = client.post(
        '/accounts',
        json={
            'username': 'diego',
            'email': 'diego.email.com',
            'password': '1234@asddfg',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_create_account_with_already_in_use_username(account, client):
    username_in_use = account.username
    response = client.post(
        '/accounts',
        json={
            'username': username_in_use,
            'email': 'new_email@mail.com',
            'password': '1234%3#dasdf',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': f'username: {username_in_use} already in use'
    }


def test_create_account_with_already_in_use_email(account, client):
    email_in_use = account.email
    response = client.post(
        '/accounts',
        json={
            'username': 'new_username',
            'email': email_in_use,
            'password': '1234%3#dasdf',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': f'email: {email_in_use} already in use'
    }


@pytest.mark.asyncio
async def test_list_accounts(client, session):
    expected_length = 10
    session.add_all(AccountFactory.create_batch(size=10))
    await session.commit()

    response = client.get('/accounts')
    accounts = response.json().get('accounts')

    assert response.status_code == HTTPStatus.OK
    assert len(accounts) == expected_length


@pytest.mark.asyncio
async def test_list_accounts_by_disabled_state(client, session):
    expected_length = 7
    session.add_all(AccountFactory.create_batch(size=5, state=State.enabled))
    session.add_all(AccountFactory.create_batch(size=7, state=State.disabled))
    await session.commit()

    response = client.get('/accounts', params={'state': 'disabled'})
    accounts = response.json().get('accounts')

    assert response.status_code == HTTPStatus.OK
    assert len(accounts) == expected_length


@pytest.mark.asyncio
async def test_list_accounts_by_enabled_state(client, session):
    expected_length = 7
    session.add_all(AccountFactory.create_batch(size=5, state=State.disabled))
    session.add_all(AccountFactory.create_batch(size=7, state=State.enabled))
    await session.commit()

    response = client.get('/accounts', params={'state': 'enabled'})
    accounts = response.json().get('accounts')

    assert response.status_code == HTTPStatus.OK
    assert len(accounts) == expected_length


def test_list_accounts_with_unknown_state(client, account):
    response = client.get('/accounts', params={'state': 'desativado'})

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_list_accounts_with_default_offset_and_limit(client, session):
    expected_length = 20
    session.add_all(AccountFactory.create_batch(size=35))
    await session.commit()

    response = client.get('/accounts')
    accounts = response.json().get('accounts')

    assert response.status_code == HTTPStatus.OK
    assert len(accounts) == expected_length


@pytest.mark.asyncio
async def test_list_accounts_with_different_offset_and_limit(client, session):
    expected_length = 5
    session.add_all(AccountFactory.create_batch(size=20))
    await session.commit()

    response = client.get('/accounts', params={'offset': 15, 'limit': 10})
    accounts = response.json().get('accounts')

    assert response.status_code == HTTPStatus.OK
    assert len(accounts) == expected_length


def test_update_account(client, account, token):
    response = client.patch(
        f'/accounts/{account.id}',
        json={
            'username': 'diegoj',
            'email': 'diegoj@email.com',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'diegoj',
        'email': 'diegoj@email.com',
        'state': 'enabled',
    }


def test_update_account_without_login(client, account):
    response = client.patch(
        f'/accounts/{account.id}',
        json={
            'username': 'diegoj',
            'email': 'diegoj@email.com',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


@pytest.mark.asyncio
async def test_update_account_not_found(client, token, session, account):
    await session.delete(account)
    await session.commit()

    response = client.patch(
        '/accounts/12',
        json={
            'username': 'diegoj',
            'email': 'diegoj@email.com',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_update_account_without_permissions(client, token):
    response = client.patch(
        '/accounts/14',
        json={
            'username': 'diegoj',
            'email': 'diegoj@email.com',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'not enough permissions to update account'
    }


@pytest.mark.asyncio
async def test_update_account_with_already_in_use_email(
    client, account, token, session
):
    new_email = 'new_account@mail.com'
    new_account = AccountFactory.create(email=new_email)
    session.add(new_account)
    await session.commit()

    response = client.patch(
        f'/accounts/{account.id}',
        json={
            'email': new_email,
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': f'email: {new_email} already in use'}


@pytest.mark.asyncio
async def test_update_account_with_already_in_use_username(
    client, account, token, session
):
    new_username = 'new_account'
    new_account = AccountFactory.create(username=new_username)
    session.add(new_account)
    await session.commit()

    response = client.patch(
        f'/accounts/{account.id}',
        json={
            'username': new_username,
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': f'username: {new_username} already in use'
    }


def test_update_account_with_invalid_email(client, account, token):
    response = client.patch(
        f'/accounts/{account.id}',
        json={
            'email': 'diegoj.email.com',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_update_account_with_invalid_password_length(client, account, token):
    response = client.patch(
        f'/accounts/{account.id}',
        json={
            'password': '123@asd',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_delete_account(client, account, token):
    response = client.delete(
        f'/accounts/{account.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_account_not_found(client, account, token, session):
    await session.delete(account)
    await session.commit()

    response = client.delete(
        '/accounts/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_delete_account_without_permissions(client, token):
    response = client.delete(
        '/accounts/12',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'not enough permissions to delete account'
    }
