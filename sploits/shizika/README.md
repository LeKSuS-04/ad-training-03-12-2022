# shizika sploits

This service contains two vulns

## Leak secret by bruteforcing last symbol of password

This piece of code is vulnerable:

```py
for secret in os.listdir('secrets'):
    if secret.startswith(secret_id) and secret.endswith(password):
        with open(f'secrets/{secret}', 'r') as f:
            secret_data = f.read()
```

Only last symbols of password are checked against provided value. So we can
bruteforce last symbol of note to acquire secret from note with known id

## RCE via command injection in feedback

This piece of code is vulnerable:

```py
os.system(f'echo "{feedback}\n" >> feedback/feedback-db.txt')
```

We can inject custom command to execute it on victiums' systems. The problem is that 
we don't immideately see the output. However, we can create note and write all information 
that we are interested in in there. After that we easily can access output of our 
command by checking that note
