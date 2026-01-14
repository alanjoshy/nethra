import pyseto
from datetime import datetime, timedelta, timezone
from typing import Dict

from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


PASETO_SECRET_KEY = b'7\x1e#J\x16\xdb\x80\xa1:\xd8*4\x11\xe1\x14\xf3\xbeE\xd7\xd1\x92U\x04\xe1Q\xb9}\x83\xbe4\xe3\x12'  # <-- replace with real 32-byte key

TOKEN_TTL_MINUTES = 60

_pasetokey = pyseto.Key.new(
    version=4,
    purpose="local",
    key=PASETO_SECRET_KEY,
)



def create_access_token(user_id: str, role: str) -> str:
    now = datetime.now(tz=timezone.utc)

    payload = {
        "sub": user_id,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=TOKEN_TTL_MINUTES)).timestamp()),
    }

    token = pyseto.encode(
        _pasetokey,
        payload,
    )

    # pyseto returns bytes
    return token.decode("utf-8")



def decode_token(token: str) -> Dict:
    try:
        decoded = pyseto.decode(
            _pasetokey,
            token,
        )

        payload = decoded.payload

        # Expiration check (mandatory)
        now_ts = int(datetime.now(tz=timezone.utc).timestamp())
        if payload.get("exp") is None or payload["exp"] < now_ts:
            raise ValueError("Token has expired")

        return payload

    except pyseto.PasetomessageError:
        raise ValueError("Invalid token")

    except Exception:
        raise ValueError("Token validation failed")
