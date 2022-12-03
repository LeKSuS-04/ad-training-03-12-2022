import re

from checklib import *


PORT = 5000


class CheckMachine:
    @property
    def url(self):
        return f'http://{self.c.host}:{PORT}'

    def __init__(self, checker: BaseChecker):
        self.c = checker
        self.session = self.c.get_initialized_session()

    def signup(self, username: str, password: str, fail_status: Status = Status.MUMBLE):
        resp = self.session.post(f'{self.url}/sign-up', data={
            'username': username,
            'password': password
        })
        self.c.assert_in(username, resp.text, "Can't sign up", fail_status)

    def login(self, username: str, password: str, fail_status: Status = Status.MUMBLE):
        resp = self.session.post(f'{self.url}/login', data={
            'username': username,
            'password': password
        })
        self.c.assert_in(username, resp.text, "Can't log in", fail_status)

    def logout(self, fail_status: Status = Status.MUMBLE):
        cookies_before_logout = len(self.session.cookies)
        self.session.get(f'{self.url}/logout')
        cookies_after_logout = len(self.session.cookies)
        self.c.assert_neq(cookies_before_logout, cookies_after_logout, "Can't log out", fail_status)

    def create_shpora(
        self, title: str, content: str, is_public: bool, is_protected: bool, 
        password: str = '', fail_status: Status = Status.MUMBLE
    ) -> str:
        resp = self.session.post(f'{self.url}/create-shpora', data={
            'title': title,
            'content': content,
            'is_public': 'on' if is_public else '',
            'is_protected': 'on' if is_protected else '',
            'password': password
        })
        self.c.assert_in(title, resp.text, "Can't create shpora", fail_status)
        self.c.assert_in(content, resp.text, "Can't create shpora", fail_status)
        if is_protected:
            self.c.assert_in(password, resp.url, "Can't create shpora", fail_status)

        url_parts = resp.url.split('=')
        for i, part in enumerate(url_parts):
            if part.endswith('id'):
                return url_parts[i+1].split('&')[0]

        self.c.cquit(fail_status, "Can't get shpora id from url", resp.url)

    def get_shpora(self, id: str, password: str = '', fail_status: Status = Status.MUMBLE) -> tuple[str, str]:
        resp = self.session.get(f'{self.url}/shpora', params={'id': id, 'password': password})
        title = re.findall(r'<h1>(.*)</h1>', resp.text)
        content = re.findall(r'<p>(.*)</p>', resp.text)
        assert_eq(not title or not content, False, "Can't access created shpora", fail_status)
        return title[0], content[0]

    def get_all_shporas(self) -> str:
        resp = self.session.get(f'{self.url}/all-shporas')
        return resp.text

    def get_my_shporas(self) -> str:
        resp = self.session.get(f'{self.url}/my-shporas')
        return resp.text
