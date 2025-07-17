from datetime import timedelta
from http import HTTPStatus

from freezegun import freeze_time


def test_login(account, client):
    response = client.post(
        '/auth/token',
        data={
            'username': account.email,
            'password': account.plain_password,
        },
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert 'expires_in' in data


def test_login_with_invalid_username(account, client):
    response = client.post(
        '/auth/token',
        data={
            'username': 'invalid',
            'password': account.plain_password,
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'invalid username or password'}


def test_login_with_invalid_password(account, client):
    response = client.post(
        '/auth/token',
        data={
            'username': account.email,
            'password': 'wrong_password',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'invalid username or password'}


def test_login_with_missing_username(client):
    response = client.post(
        '/auth/token',
        data={
            'password': 'any_password',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_login_with_missing_password(client):
    response = client.post(
        '/auth/token',
        data={
            'username': 'any_account',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_login_with_disabled_account(): ...


def test_refresh_token(account, client):
    with freeze_time('2025-07-10 12:00:00') as frozen_time:
        response_login = client.post(
            '/auth/token',
            data={
                'username': account.email,
                'password': account.plain_password,
            },
        )
        data = response_login.json()

        frozen_time.tick(timedelta(seconds=290))

        response_refresh = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {data["access_token"]}'},
        )

        refreshed_data = response_refresh.json()

    assert response_refresh.status_code == HTTPStatus.OK
    assert 'access_token' in refreshed_data
    assert 'token_type' in refreshed_data
    assert 'expires_in' in refreshed_data
    assert data['access_token'] != refreshed_data['access_token']


def test_refresh_token_with_expired_token(account, client):
    with freeze_time('2025-07-10 12:00:00') as frozen_time:
        response_login = client.post(
            '/auth/token',
            data={
                'username': account.email,
                'password': account.plain_password,
            },
        )
        data = response_login.json()

        frozen_time.tick(timedelta(seconds=301))

        response_refresh = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {data["access_token"]}'},
        )

    assert response_refresh.status_code == HTTPStatus.UNAUTHORIZED
    assert response_refresh.json() == {
        'detail': 'Could not validate credentials'
    }


def test_refresh_token_missing_authorization_header(client):
    response_refresh = client.post('/auth/refresh_token')

    assert response_refresh.status_code == HTTPStatus.UNAUTHORIZED
    assert response_refresh.json() == {'detail': 'Not authenticated'}
