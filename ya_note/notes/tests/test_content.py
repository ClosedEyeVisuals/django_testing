from .base_t import BaseTest
from notes.forms import NoteForm


class TestContent(BaseTest):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_notes_list_for_different_users(self):
        users_assertions = (
            (self.author_client, True),
            (self.reader_client, False)
        )
        for user, note_in_list in users_assertions:
            response = user.get(self.LIST_URL)
            object_list = response.context['object_list']
            self.assertIs(self.note in object_list, note_in_list)

    def test_note_add_and_edit_has_form(self):
        urls = (self.ADD_URL, self.EDIT_URL)
        for url in urls:
            with self.subTest(name=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
