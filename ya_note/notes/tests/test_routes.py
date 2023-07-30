from http import HTTPStatus
from notes.models import Note
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='User')
        cls.reader = User.objects.create(username='Noname')
        cls.note = Note.objects.create(
            title='Title',
            text='Text',
            author=cls.author,
            slug='slug'
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail(self):
        user_status = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND)
        )
        for user, status in user_status:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:detail', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_authoriz(self):
        user_status = (
            (self.author, HTTPStatus.OK),
        )
        for user, status in user_status:
            self.client.force_login(user)
            for name in ('notes:add', 'notes:success'):
                with self.subTest(user=user, name=name):
                    url = reverse(name)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymos(self):
        login_url = reverse('users:login')
        for name in ('notes:detail', 'notes:edit', 'notes:delete'):
            url = reverse(name, args=(self.note.slug,))
            redirect_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            # Проверяем, что редирект приведёт именно на указанную ссылку.
            self.assertRedirects(response, redirect_url)

    def test_another_redirect_for_anonymos(self):
        login_url = reverse('users:login')
        for name in ('notes:add', 'notes:list', 'notes:success'):
            url = reverse(name)
            redirect_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            # Проверяем, что редирект приведёт именно на указанную ссылку.
            self.assertRedirects(response, redirect_url)
