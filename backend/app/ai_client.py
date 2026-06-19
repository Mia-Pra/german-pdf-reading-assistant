from collections.abc import Sequence
from typing import Any

import httpx

from app.config import Settings, get_settings


class AIClientError(RuntimeError):
    pass


class AIConfigurationError(AIClientError):
    pass


class AIProviderError(AIClientError):
    pass


class AIResponseError(AIClientError):
    pass


def _chat_completions_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/chat/completions"


def _normalize_messages(messages: Sequence[dict[str, str]]) -> list[dict[str, str]]:
    normalized = []
    for message in messages:
        role = message.get("role", "").strip()
        content = message.get("content", "").strip()
        if not role or not content:
            raise AIResponseError("AI messages must include non-empty role and content.")
        normalized.append({"role": role, "content": content})
    return normalized


class AIClient:
    def __init__(
        self,
        settings: Settings | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.http_client = http_client

    def chat(
        self,
        messages: Sequence[dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> str:
        try:
            self.settings.require_ai_config()
        except RuntimeError as exc:
            raise AIConfigurationError(str(exc)) from exc

        payload: dict[str, Any] = {
            "model": self.settings.openai_model,
            "messages": _normalize_messages(messages),
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }

        client = self.http_client or httpx.Client(timeout=60)
        should_close = self.http_client is None

        try:
            response = client.post(
                _chat_completions_url(self.settings.openai_base_url),
                headers=headers,
                json=payload,
            )
        except httpx.HTTPError as exc:
            raise AIProviderError(f"AI provider request failed: {exc}") from exc
        finally:
            if should_close:
                client.close()

        if response.status_code >= 400:
            raise AIProviderError(
                f"AI provider returned HTTP {response.status_code}: {response.text}"
            )

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise AIResponseError("AI provider returned an unexpected response format.") from exc

        if not isinstance(content, str) or not content.strip():
            raise AIResponseError("AI provider returned an empty response.")

        return content.strip()


def create_ai_client() -> AIClient:
    return AIClient()
