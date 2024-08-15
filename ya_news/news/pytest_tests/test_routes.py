import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('news_pk_for_args')),
        ('news:home', None),
        ('users:signup', None),
        ('users:login', None),
        ('users:logout', None),
    )
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirects(client, name, comment_pk_for_args):
    login_url = reverse('users:login')
    url = reverse(name, args=comment_pk_for_args)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
@pytest.mark.parametrize(
    'param_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND)
    )
)
def test_availability_for_comment_edit_and_delete(
        param_client, expected_status, name, comment_pk_for_args):
    url = reverse(name, args=comment_pk_for_args)
    response = param_client.get(url)
    assert response.status_code == expected_status
