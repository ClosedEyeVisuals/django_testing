import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, news_pk_for_args, form_data):

    url = reverse('news:detail', args=news_pk_for_args)
    client.post(url, data=form_data)
    comment_count = Comment.objects.count()
    assert comment_count == 0


def test_user_can_create_comment(
        author_client, author, news, news_pk_for_args, form_data):

    url = reverse('news:detail', args=news_pk_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, (url + '#comments'))
    comment_count = Comment.objects.count()
    assert comment_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_use_bad_words(
        author_client, news_pk_for_args, bad_word_data):

    url = reverse('news:detail', args=news_pk_for_args)
    response = author_client.post(url, data=bad_word_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author_client, comment,
        comment_pk_for_args, news_pk_for_args, form_data):

    url = reverse('news:edit', args=comment_pk_for_args)
    response = author_client.post(url, data=form_data)
    redirect_url = reverse('news:detail', args=news_pk_for_args) + '#comments'
    assertRedirects(response, redirect_url)
    comment = Comment.objects.get()
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_comment(
        reader_client, comment, comment_pk_for_args, form_data):

    url = reverse('news:edit', args=comment_pk_for_args)
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_user_can_delete_comment(
        author_client, comment_pk_for_args, news_pk_for_args):

    url = reverse('news:delete', args=comment_pk_for_args)
    response = author_client.post(url)
    redirect_url = reverse('news:detail', args=news_pk_for_args) + '#comments'
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(
        reader_client, comment_pk_for_args):

    url = reverse('news:delete', args=comment_pk_for_args)
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
