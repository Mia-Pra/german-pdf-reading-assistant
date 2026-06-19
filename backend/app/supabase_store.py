from typing import Any
from urllib.parse import quote

import httpx
from fastapi import HTTPException, status

from app.config import get_settings


def _settings():
    settings = get_settings()
    if not settings.has_supabase_config:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase is not configured on the backend.",
        )
    return settings


def _service_headers(*, prefer: str | None = None) -> dict[str, str]:
    settings = _settings()
    headers = {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers


def _request(
    method: str,
    path: str,
    *,
    params: dict[str, str] | None = None,
    json: Any = None,
    content: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    settings = _settings()
    request_headers = _service_headers()
    if headers:
        request_headers.update(headers)
    try:
        response = httpx.request(
            method,
            f"{settings.supabase_url}{path}",
            params=params,
            json=json,
            content=content,
            headers=request_headers,
            timeout=30,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Persistent storage is unavailable.",
        ) from exc
    if response.status_code >= 400:
        detail = "Persistent storage request failed."
        try:
            payload = response.json()
            detail = payload.get("message") or payload.get("error") or detail
        except ValueError:
            pass
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        )
    return response


def get_current_document(user_id: str) -> dict[str, Any] | None:
    response = _request(
        "GET",
        "/rest/v1/current_documents",
        params={
            "user_id": f"eq.{user_id}",
            "select": "document_data",
            "limit": "1",
        },
    )
    rows = response.json()
    return rows[0]["document_data"] if rows else None


def save_current_document(user_id: str, document: dict[str, Any]) -> None:
    _request(
        "POST",
        "/rest/v1/current_documents",
        params={"on_conflict": "user_id"},
        json={
            "user_id": user_id,
            "document_id": document["document_id"],
            "filename": document["filename"],
            "storage_path": document["storage_path"],
            "document_data": document,
        },
        headers={
            "Prefer": "resolution=merge-duplicates,return=minimal",
            "Content-Type": "application/json",
        },
    )


def upload_pdf(user_id: str, object_name: str, contents: bytes) -> str:
    settings = _settings()
    storage_path = f"{user_id}/{object_name}"
    encoded_path = quote(storage_path, safe="/")
    _request(
        "POST",
        f"/storage/v1/object/{settings.supabase_storage_bucket}/{encoded_path}",
        content=contents,
        headers={
            "Content-Type": "application/pdf",
            "x-upsert": "true",
        },
    )
    return storage_path


def create_pdf_signed_url(storage_path: str, expires_in: int = 3600) -> str:
    settings = _settings()
    encoded_path = quote(storage_path, safe="/")
    response = _request(
        "POST",
        f"/storage/v1/object/sign/{settings.supabase_storage_bucket}/{encoded_path}",
        json={"expiresIn": expires_in},
        headers={"Content-Type": "application/json"},
    )
    signed_path = response.json().get("signedURL", "")
    if not signed_path:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="PDF preview URL could not be generated.",
        )
    if signed_path.startswith("http"):
        return signed_path
    if signed_path.startswith("/"):
        return f"{settings.supabase_url}/storage/v1{signed_path}"
    return f"{settings.supabase_url}/storage/v1/{signed_path.lstrip('/')}"


def list_vocabulary(user_id: str) -> list[dict[str, Any]]:
    response = _request(
        "GET",
        "/rest/v1/vocabulary",
        params={
            "user_id": f"eq.{user_id}",
            "select": "id,word,lemma,part_of_speech,plural,translation,example_sentence,source_page",
            "order": "created_at.asc",
        },
    )
    return response.json()


def add_vocabulary(user_id: str, item: dict[str, Any]) -> dict[str, Any] | None:
    response = _request(
        "POST",
        "/rest/v1/vocabulary",
        json={**item, "user_id": user_id},
        headers={
            "Prefer": "return=representation",
            "Content-Type": "application/json",
        },
    )
    rows = response.json()
    return rows[0] if rows else None


def delete_vocabulary(user_id: str, item_id: str) -> bool:
    response = _request(
        "DELETE",
        "/rest/v1/vocabulary",
        params={"user_id": f"eq.{user_id}", "id": f"eq.{item_id}"},
        headers={"Prefer": "return=representation"},
    )
    return bool(response.json())


def get_full_translation(user_id: str, document_id: str) -> dict[str, Any] | None:
    response = _request(
        "GET",
        "/rest/v1/full_translations",
        params={
            "user_id": f"eq.{user_id}",
            "document_id": f"eq.{document_id}",
            "select": "payload",
            "limit": "1",
        },
    )
    rows = response.json()
    return rows[0]["payload"] if rows else None


def save_full_translation(
    user_id: str,
    document_id: str,
    payload: dict[str, Any],
) -> None:
    _request(
        "POST",
        "/rest/v1/full_translations",
        params={"on_conflict": "user_id"},
        json={
            "user_id": user_id,
            "document_id": document_id,
            "payload": payload,
        },
        headers={
            "Prefer": "resolution=merge-duplicates,return=minimal",
            "Content-Type": "application/json",
        },
    )
