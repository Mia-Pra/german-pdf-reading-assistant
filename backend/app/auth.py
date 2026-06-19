from dataclasses import dataclass

import httpx
from fastapi import Header, HTTPException, status

from app.config import get_settings
from app.http_client import get_http_client


@dataclass(frozen=True)
class AuthenticatedUser:
    id: str
    email: str


def _supabase_unavailable() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Supabase is not configured on the backend.",
    )


def get_authenticated_user(
    authorization: str | None = Header(default=None),
) -> AuthenticatedUser:
    settings = get_settings()
    if not settings.has_supabase_config:
        raise _supabase_unavailable()
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sign in is required.",
        )

    token = authorization.split(" ", 1)[1].strip()
    try:
        response = get_http_client().get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={
                "apikey": settings.supabase_anon_key,
                "Authorization": f"Bearer {token}",
            },
            timeout=15,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is unavailable.",
        ) from exc

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session is invalid or expired. Sign in again.",
        )

    payload = response.json()
    user_id = str(payload.get("id", "")).strip()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user id is missing.",
        )
    return AuthenticatedUser(id=user_id, email=str(payload.get("email", "")))
