from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify


from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст'
    NOTE_SLUG = 'some-thing'

    # FORM_TITLE = 'Header'
    # FORM_TEXT = 'Text'
    # FORM_SLUG = 'some-slug'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='censuby')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        # cls.note = Note.objects.create(
        #     title=cls.NOTE_TITLE,
        #     text=cls.NOTE_TEXT,
        #     slug=cls.NOTE_SLUG,
        #     author=cls.user
        # )
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }
        cls.success_url = reverse('notes:success')

    def test_user_can_create_note(self):
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.user)

    def test_anonymous_user_cant_create_note(self):
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={self.url}'
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_not_unique_slug(self):
        self.note = Note.objects.create(
            title='Какой-то заголовок',
            text='Какой-то текст',
            slug='some-slug',
            author=self.user
        )
        self.form_data['slug'] = self.note.slug
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=self.note.slug + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.user_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст'
    NOTE_SLUG = 'some-thing'

    NEW_NOTE_TITLE = 'Новый заголовок'
    NEW_NOTE_TEXT = 'Новый текст'
    NEW_NOTE_SLUG = 'new-slug'

    @classmethod
    def setUpTestData(cls):
        cls.success_url = reverse('notes:success')
        cls.author = User.objects.create(username='censuby')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='chitatel')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG,
        }

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NEW_NOTE_SLUG)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
