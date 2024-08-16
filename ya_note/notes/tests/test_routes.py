from http import HTTPStatus

from .base_t import BaseTest


class TestRoutes(BaseTest):

    def test_pages_availability_for_anonymous(self):
        urls = (
            self.HOME_URL,
            self.LOGIN_URL,
            self.LOGOUT_URL,
            self.SIGNUP_URL,
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_authorized_user(self):
        urls = (
            self.ADD_URL,
            self.SUCCESS_URL,
            self.LIST_URL,
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_detail_edit_and_delete(self):
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND)
        )
        for user, status in users_statuses:
            for url in (self.DETAIL_URL, self.EDIT_URL, self.DELETE_URL):
                with self.subTest(user=user, name=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous(self):
        urls = (
            self.ADD_URL,
            self.LIST_URL,
            self.SUCCESS_URL,
            self.EDIT_URL,
            self.DETAIL_URL,
            self.DELETE_URL,
        )
        for url in urls:
            with self.subTest(name=url):
                redirect_url = f'{self.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
