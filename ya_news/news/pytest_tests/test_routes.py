from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

HOME_URL = pytest.lazy_fixture('home_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
READER_CLIENT = pytest.lazy_fixture('reader_client')


@pytest.mark.parametrize(
    'url',
    (DETAIL_URL, HOME_URL, SIGNUP_URL, LOGIN_URL, LOGOUT_URL),
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous(client, url):
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url',
    (EDIT_URL, DELETE_URL)
)
def test_redirects(client, url, login_url):
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)


@pytest.mark.parametrize(
    'url',
    (EDIT_URL, DELETE_URL)
)
@pytest.mark.parametrize(
    'param_client, expected_status',
    (
        (AUTHOR_CLIENT, HTTPStatus.OK),
        (READER_CLIENT, HTTPStatus.NOT_FOUND)
    )
)
def test_availability_for_comment_edit_and_delete(
        param_client, expected_status, url):
    response = param_client.get(url)
    assert response.status_code == expected_status
