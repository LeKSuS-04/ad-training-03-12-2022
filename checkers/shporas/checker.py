#!/usr/bin/env python

import sys
import requests

from checklib import *
from shporas_lib import CheckMachine


class Checker(BaseChecker):
    vulns: int = 9
    timeout: int = 10
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.chm = CheckMachine(self)

    def check(self):
        username = rnd_username()
        password = rnd_password()

        # Check auth
        self.chm.signup(username, password)
        self.chm.logout()
        self.chm.login(username, password)

        # Create public unprotected shpora
        title = rnd_string(20)
        content = rnd_string(100)
        shpora_id = self.chm.create_shpora(title, content, True, False)
        title_resp, content_resp = self.chm.get_shpora(shpora_id)
        assert_eq(title_resp, title, "Shpora title changed")
        assert_eq(content_resp, content, "Shpora title changed")
        assert_in(shpora_id, self.chm.get_all_shporas(), "Don't see public shpora in list of public shporas")
        assert_in(shpora_id, self.chm.get_my_shporas(), "Don't see public shpora in list of my shporas")

        # Create private unprotected shpora
        title = rnd_string(20)
        content = rnd_string(100)
        shpora_id = self.chm.create_shpora(title, content, False, False)
        title_resp, content_resp = self.chm.get_shpora(shpora_id)
        assert_nin(shpora_id, self.chm.get_all_shporas(), "Can see private shpora in list of public shporas")
        assert_in(shpora_id, self.chm.get_my_shporas(), "Don't see private shpora in list of my shporas")

        # Create private protected shpora
        title = rnd_string(20)
        content = rnd_string(100)
        shpora_password = rnd_password()
        shpora_id = self.chm.create_shpora(title, content, False, True, shpora_password)
        title_resp, content_resp = self.chm.get_shpora(shpora_id)
        assert_nin(shpora_id, self.chm.get_all_shporas(), "Can see private shpora in list of public shporas")
        assert_in(shpora_id, self.chm.get_my_shporas(), "Can't see private shpora in list of my shporas")

        self.cquit(Status.OK)


    def put(self, flag_id: str, flag: str, vuln: str):
        username = rnd_username()
        password = rnd_password()
        title = rnd_string(20)
        shpora_password = rnd_password()
        self.chm.signup(username, password)
        
        # Public shpora with flag in content
        if vuln == '1':
            shpora_id = self.chm.create_shpora(title, flag, True, False)
            self.cquit(Status.OK, username, f'{username}:{password}:{shpora_id}:{shpora_password}')

        # Private unprotected shpora with flag in content
        if vuln in '23':
            shpora_id = self.chm.create_shpora(title, flag, False, False)
            self.cquit(Status.OK, username, f'{username}:{password}:{shpora_id}:{shpora_password}')
    
        # Private protected shpora with flag in content
        if vuln in '456':
            shpora_id = self.chm.create_shpora(title, flag, False, True, shpora_password)
            self.cquit(Status.OK, username, f'{username}:{password}:{shpora_id}:{shpora_password}')
        
        # User with no public shporas   
        if vuln in '789':
            self.cquit(Status.OK, username, f'{username}:{password}:_:{shpora_password}')

        self.cquit(Status.ERROR, 'Checker error', f'Unexpected vuln value: {vuln}')


    def get(self, flag_id: str, flag: str, vuln: str):
        username, password, shpora_id, shpora_password = flag_id.split(':')
        self.chm.login(username, password)
        if vuln in '123456':
            _, content_resp = self.chm.get_shpora(shpora_id, shpora_password)
            assert_eq(content_resp, flag, "Corrupted flag", Status.CORRUPT)
        
        self.cquit(Status.OK)


if __name__ == '__main__':
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except requests.exceptions.ConnectionError as e:
        cquit(Status.DOWN, "Can't access service", str(e))
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)