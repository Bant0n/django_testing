from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):
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

    def test_task_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('notes:list'))
        first_object = response.context['object_list'][0]
        task_title_0 = first_object.title
        task_text_0 = first_object.text
        task_slug_0 = first_object.slug
        self.assertEqual(task_title_0, 'Title')
        self.assertEqual(task_text_0, 'Text')
        self.assertEqual(task_slug_0, 'slug')

    def test_authorized_client_has_form(self):
        response = self.authorized_client.get(reverse('notes:add'))
        self.assertIn('form', response.context)

    def test_a_authorized_client_has_form(self):
        response = self.authorized_client.get(reverse(
            'notes:edit', args=(self.note.slug,))
        )
        self.assertIn('form', response.context)
