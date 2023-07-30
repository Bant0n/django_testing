import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    # Предварительно оборачиваем имена фикстур
    # в вызов функции pytest.lazy_fixture().
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
    parametrized_client, name, comment, expected_status
):
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    # Предварительно оборачиваем имена фикстур
    # в вызов функции pytest.lazy_fixture().
    (
        (pytest.lazy_fixture('client'), HTTPStatus.FOUND),
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_anon_users(
    parametrized_client, name, comment, expected_status
):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = parametrized_client.get(url)
    assertRedirects(response, expected_url)
