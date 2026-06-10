from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from jose import jwt, JWTError

from app.core.config import settings

ALGORITHM = "HS256"


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()

    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc)
        + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=ALGORITHM
    )


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[ALGORITHM]
        )

        if not payload.get("sub"):
            return None

        return payload

    except JWTError:
        return None

    except Exception:
        return None
