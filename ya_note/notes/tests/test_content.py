from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='censuby')
        cls.reader = User.objects.create(username='botanic')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='some-thing',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_notes_list_for_different_users(self):
        users_assertions = (
            (self.author, True),
            (self.reader, False)
        )
        for user, note_in_list in users_assertions:
            self.client.force_login(user)
            response = self.client.get(self.URL)
            object_list = response.context['object_list']
            self.assertIs(self.note in object_list, note_in_list)

    def test_note_add_and_edit_has_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
