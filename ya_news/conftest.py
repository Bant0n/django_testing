import pytest
# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import News, Comment
from datetime import datetime, timedelta
from django.conf import settings


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        text='Текст заметки',
        author=author,
    )


@pytest.fixture
def news_list():
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment_list(news, author):
    now = datetime.today()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
