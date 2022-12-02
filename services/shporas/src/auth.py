import base64
import json


def encode_session(username: str) -> str:
    return base64.b64encode(json.dumps({'user': username}).encode()).decode()


def decode_session(session: str) -> str | None:
    try:
        return json.loads(base64.b64decode(session).decode())['user']
    except Exception:
        return None
