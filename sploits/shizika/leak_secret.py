#!/usr/bin/env python

import sys
from pwn import *
from string import ascii_letters, digits

host = sys.argv[1]
hint = sys.argv[2]

r = remote(host, 1337)


for c in ascii_letters + digits:
    r.recvuntil(b'> ')
    r.sendline(b'2')
    r.recvuntil(b': ')
    r.sendline(hint.encode())
    r.recvuntil(b': ')
    r.sendline(c.encode())
    secret = r.recvuntil(b'\n\n').decode()
    print(secret, flush=True)


