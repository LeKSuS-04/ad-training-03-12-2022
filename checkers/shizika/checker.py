#!/usr/bin/env python

import re
import sys

from pwn import *
from checklib import *


PORT = 1337
context.log_level = 'critical'


class Checker(BaseChecker):
    vulns: int = 2
    timout: int = 10
    uses_attack_data: bool = False

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self._pwn_sessions: list[remote] = []

    def get_session(self) -> remote:
        try:
            r = remote(self.host, PORT)
            r.timeout = Checker.timeout
        except PwnlibException as e:
            cquit(Status.DOWN, "Can't connect", str(e))
        self._pwn_sessions.append(r)
        return r

    def store_secret(self, r: remote, content: str, password: str, fail_status: Status = Status.MUMBLE) -> str:
        r.recvuntil(b'> ')
        r.sendline(b'1')
        r.recvuntil(b': ')
        r.sendline(content.encode())
        r.recvuntil(b': ')
        r.sendline(password.encode())
        data = r.recvuntil(b'\n\n').decode()
        secret_id_matches = re.findall(r'ID of your secret is ([a-zA-Z0-9]*)\n', data)
        self.assert_neq(len(secret_id_matches), 0, "Can't create secret", fail_status)
        return secret_id_matches[0]

    def get_secret(self, r: remote, secret_id: str, password: str, fail_status: Status = Status.MUMBLE) -> str:
        r.recvuntil(b'> ')
        r.sendline(b'2')
        r.recvuntil(b': ')
        r.sendline(secret_id.encode())
        r.recvuntil(b': ')
        r.sendline(password.encode())
        r.recvuntil((b': ', b':('))
        secret = r.recvuntil(b'\n\n', drop=True).decode()
        self.assert_neq(secret, '', "Can't access secret", fail_status)
        return secret

    def leave_feedback(self, r: remote, feedback: str, fail_status: Status = Status.MUMBLE):
        r.recvuntil(b'>')
        r.sendline(b'3')
        r.recvuntil(b': ')
        r.sendline(b'yes')
        r.recvuntil(b': ')
        r.sendline(feedback.encode())
        data = r.recvuntil(b'Bye!').decode()
        self.assert_in('Thank you for your feedback', data, "Can't leave feedback", fail_status)

    def check(self):
        r = self.get_session()

        secret_content = rnd_string(20)
        secret_password = rnd_string(20)
        feedback = rnd_string(100)

        secret_id = self.store_secret(r, secret_content, secret_password)
        self.get_secret(r, secret_id, secret_password)
        self.leave_feedback(r, feedback)
        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        r = self.get_session()

        if vuln == '1':
            secret_password = rnd_string(20)
            secret_id = self.store_secret(r, flag, secret_password)
            self.cquit(Status.OK, secret_id, f'{secret_id}:{secret_password}')
        elif vuln == '2':
            self.leave_feedback(r, flag)
            self.cquit(Status.OK)
        else:
            self.cquit(Status.ERROR, 'Checker error', f'Unexpected vuln value: {vuln}')

    def get(self, flag_id: str, flag: str, vuln: str):
        if vuln == '2':
            self.cquit(Status.OK)

        r = self.get_session()
        secret_id, secret_password = flag_id.split(':')
        secret = self.get_secret(r, secret_id, secret_password)
        self.assert_eq(secret, flag, "Secret value is invalid", Status.CORRUPT)

        self.cquit(Status.OK)

    def cquit(self, status: Status, public: str = '', private: str | None = None):
        for sess in self._pwn_sessions:
            sess.close()
        self._pwn_sessions = []

        super().cquit(status, public, private)


if __name__ == '__main__':
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
