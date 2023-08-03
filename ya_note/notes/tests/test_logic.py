# news/tests/test_logic.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestCommentCreation(TestCase):
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
        cls.url = reverse('notes:add')

    def test_anonymous_user_cant_create_comment(self):
        self.client.post(self.url, data=self.form_data, follow=True)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, 1)

    def test_auth_user_can_create_comment(self):
        self.authorized_client.post(self.url, data=self.form_data)
        comments_count = Note.objects.count()
        self.assertTrue(
            Note.objects.filter(
                slug='slug-test',
                text=self.COMMENT_TEXT,
                title='qwe',
                author=self.user,
            ).exists()
        )
        self.assertEqual(comments_count, 2)


class TestCommentEditDelete(TestCase):

    COMMENT_TEXT = 'Текст комментария'
    NEW_COMMENT_TEXT = 'Обновлённый комментарий'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='auth')
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            author=cls.user,
            slug='slug'
        )
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.notauthor_client = Client()
        cls.author_client.force_login(cls.user)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'text': cls.NEW_COMMENT_TEXT}

    def test_author_can_delete_comment(self):
        self.author_client.delete(self.delete_url)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, 0)

    def test_reader_can_delete_comment(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, 1)

    def test_author_can_edit_comment(self):
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.text, self.NEW_COMMENT_TEXT)

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
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
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
