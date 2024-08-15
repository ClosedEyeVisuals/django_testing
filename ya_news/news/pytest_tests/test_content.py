import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count_on_home_page(client, all_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order_on_home_page(client, all_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order_on_detail_page(
        client, news_pk_for_args, all_comments):

    url = reverse('news:detail', args=news_pk_for_args)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_user_has_no_form_on_detail_page(client, news_pk_for_args):
    url = reverse('news:detail', args=news_pk_for_args)
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_user_has_form_on_detail_page(
        admin_client, news_pk_for_args):

    url = reverse('news:detail', args=news_pk_for_args)
    response = admin_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
