from http import HTTPStatus

from pytils.translit import slugify

from .base_t import BaseTest
from notes.forms import WARNING
from notes.models import Note


class TestNoteCreation(BaseTest):

    NEW_TITLE = 'Новый заголовок'
    NEW_TEXT = 'Новый текст'
    NEW_SLUG = 'new-slug'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT,
            'slug': cls.NEW_SLUG
        }

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.author_client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NEW_TITLE)
        self.assertEqual(note.text, self.NEW_TEXT)
        self.assertEqual(note.slug, self.NEW_SLUG)
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        notes_start_count = Note.objects.count()
        redirect_url = f'{self.LOGIN_URL}?next={self.ADD_URL}'
        response = self.client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, redirect_url)
        notes_finish_count = Note.objects.count()
        self.assertEqual(notes_finish_count, notes_start_count)

    def test_not_unique_slug(self):
        notes_start_count = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.ADD_URL, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=self.note.slug + WARNING
        )
        notes_finish_count = Note.objects.count()
        self.assertEqual(notes_finish_count, notes_start_count)

    def test_empty_slug(self):
        Note.objects.all().delete()
        self.form_data.pop('slug')
        response = self.author_client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(BaseTest):

    EDITED_NOTE_TITLE = 'Измененный заголовок'
    EDITED_NOTE_TEXT = 'Измененный текст'
    EDITED_NOTE_SLUG = 'edited-slug'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': cls.EDITED_NOTE_TITLE,
            'text': cls.EDITED_NOTE_TEXT,
            'slug': cls.EDITED_NOTE_SLUG,
        }

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.EDIT_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.EDITED_NOTE_TITLE)
        self.assertEqual(note_from_db.text, self.EDITED_NOTE_TEXT)
        self.assertEqual(note_from_db.slug, self.EDITED_NOTE_SLUG)
        self.assertEqual(note_from_db.author, self.author)

    def test_author_can_delete_note(self):
        notes_start_count = Note.objects.count()
        response = self.author_client.delete(self.DELETE_URL)
        self.assertRedirects(response, self.SUCCESS_URL)
        notes_finish_count = Note.objects.count()
        self.assertEqual(notes_finish_count, notes_start_count - 1)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(note_from_db.author, self.note.author)

    def test_user_cant_delete_note_of_another_user(self):
        notes_start_count = Note.objects.count()
        response = self.reader_client.delete(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_finish_count = Note.objects.count()
        self.assertEqual(notes_finish_count, notes_start_count)
