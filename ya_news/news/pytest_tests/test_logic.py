from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, detail_url, form_data):

    client.post(detail_url, data=form_data)
    comment_count = Comment.objects.count()
    assert comment_count == 0


def test_user_can_create_comment(
        author_client, author, news, detail_url, form_data):

    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, (detail_url + '#comments'))
    comment_count = Comment.objects.count()
    assert comment_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_use_bad_words(
        author_client, detail_url, bad_word_data):

    response = author_client.post(detail_url, data=bad_word_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author_client, comment,
        edit_url, detail_url, form_data):

    response = author_client.post(edit_url, data=form_data)
    redirect_url = detail_url + '#comments'
    assertRedirects(response, redirect_url)
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == form_data['text']
    assert comment_from_db.news == comment.news
    assert comment_from_db.author == comment.author


def test_other_user_cant_edit_comment(
        reader_client, comment, edit_url, form_data):

    response = reader_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author


def test_user_can_delete_comment(
        author_client, delete_url, detail_url):

    response = author_client.post(delete_url)
    redirect_url = detail_url + '#comments'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(
        reader_client, edit_url):

    response = reader_client.post(edit_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
