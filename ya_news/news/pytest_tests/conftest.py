import pytest
from datetime import datetime as dt, timedelta

from django.conf import settings
from django.test import Client
from django.utils import timezone as tz

from news.forms import BAD_WORDS
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='censuby')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='botanic')


@pytest.fixture
def news():
    news = News.objects.create(title='Заголовок', text='Текст')
    return news


@pytest.fixture
def news_pk_for_args(news):
    return (news.pk,)


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def comment_pk_for_args(comment):
    return (comment.pk,)


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def all_news():
    today = dt.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]

    return News.objects.bulk_create(all_news)


@pytest.fixture
def all_comments(news, author):

    all_comments = []
    now = tz.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        all_comments.append(comment)

    return all_comments


@pytest.fixture
def form_data():
    return {'text': 'Какой-то текст комментария'}


@pytest.fixture
def bad_word_data():
    return {'text': f'Что-то {BAD_WORDS[1]} кто-то'}
