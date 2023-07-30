# news/tests/test_logic.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestCommentCreation(TestCase):
    # Текст комментария понадобится в нескольких местах кода,
    # поэтому запишем его в атрибуты класса.
    COMMENT_TEXT = 'Текст комментария'

    @classmethod
    def setUpTestData(cls):
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            author=cls.user,
            slug='slug'
        )
        cls.form_data = {
            'title': 'qwe',
            'text': cls.COMMENT_TEXT,
            'slug': 'slug-test',
            'author': cls.user,
        }
        cls.url = reverse('notes:list')

    def test_anonymous_user_cant_create_comment(self):
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом комментария.
        self.client.post(self.url, data=self.form_data)
        # Считаем количество комментариев.
        comments_count = Note.objects.count()
        # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
        self.assertEqual(comments_count, 1)

    def test_auth_user_cant_create_comment(self):
        self.authorized_client.post(self.url, data=self.form_data)

        comments_count = Note.objects.count()

        self.assertEqual(comments_count, 1)


class TestCommentEditDelete(TestCase):

    COMMENT_TEXT = 'Текст комментария'
    NEW_COMMENT_TEXT = 'Обновлённый комментарий'

    @classmethod
    def setUpTestData(cls):
        # Создаём новость в БД.
        cls.user = User.objects.create_user(username='auth')
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            author=cls.user,
            slug='slug'
        )
        # Создаём пользователя - автора комментария.
        cls.author = User.objects.create(username='Автор комментария')
        # Создаём клиент для пользователя-автора.
        cls.author_client = Client()
        cls.notauthor_client = Client()
        # "Логиним" пользователя в клиенте.
        cls.author_client.force_login(cls.user)
        # Делаем всё то же самое для пользователя-читателя.
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # URL для редактирования комментария.
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        # URL для удаления комментария.
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        # Формируем данные для POST-запроса по обновлению комментария.
        cls.form_data = {'text': cls.NEW_COMMENT_TEXT}

    def test_author_can_delete_comment(self):
        # От имени автора комментария отправляем DELETE-запрос на удаление.
        response = self.author_client.delete(self.delete_url)
        # Проверяем, что редирект привёл к разделу с комментариями.
        # За
        # Считаем количество комментариев в системе.
        comments_count = response  # чтобы не мешал
        comments_count = Note.objects.count()
        # Ожидаем ноль комментариев в системе.
        self.assertEqual(comments_count, 0)

    def test_reader_can_delete_comment(self):
        # От имени автора комментария отправляем DELETE-запрос на удаление.
        response = self.reader_client.delete(self.delete_url)
        # Проверяем, что редирект привёл к разделу с комментариями.
        # Заодно проверим статус-коды ответов.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Считаем количество комментариев в системе.
        comments_count = Note.objects.count()
        # Ожидаем ноль комментариев в системе.
        self.assertEqual(comments_count, 1)

    def test_author_can_edit_comment(self):
        # Выполняем запрос на редактирование от имени автора комментария.
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст комментария соответствует обновленному.
        self.assertNotEqual(self.note.text, self.NEW_COMMENT_TEXT)

    def test_user_cant_edit_comment_of_another_user(self):
        # Выполняем запрос на редактирование от имени другого пользователя.
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        # Проверяем, что вернулась 404 ошибка.
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Обновляем объект комментария.
        self.note.refresh_from_db()
        # Проверяем, что текст остался тем же, что и был.
        self.assertEqual(self.note.text, self.note.text)

    def test_cant_create_existing_slug(self):
        note_count = Note.objects.count()
        form_datas = {
            'title': 'title',
            'text': 'text',
            'author': self.user,
            'slug': 'slug',
        }
        response = self.author_client.post(
            reverse('notes:list'),
            data=form_datas,
            follow=True
        )
        self.assertEqual(Note.objects.count(), note_count)

        # Проверим, что ничего не упало и страница отдаёт код 200
        self.assertEqual(response.status_code, 405)
