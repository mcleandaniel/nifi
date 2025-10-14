"""Authentication helpers."""

from __future__ import annotations

from urllib.parse import urljoin

import httpx

# Allow tests to swap out the HTTP client factory without touching the module namespace
_client_factory = httpx.Client

from .config import AuthSettings


class AuthenticationError(RuntimeError):
    """Raised when NiFi authentication fails."""


def obtain_access_token(settings: AuthSettings) -> str:
    """Request a bearer token from NiFi's ``/access/token`` endpoint."""

    base = str(settings.base_url).rstrip("/")
    token_url = f"{base}/access/token"
    verify_flag = settings.verify_ssl
    if isinstance(verify_flag, str):
        verify_flag = verify_flag.lower() not in {"false", "0", "no", "off"}
    with _client_factory(verify=verify_flag, timeout=settings.timeout) as client:
        response = client.post(
            token_url,
            data={"username": settings.username, "password": settings.password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:  # pragma: no cover - simple rewrap
            raise AuthenticationError(
                f"Failed to obtain token ({exc.response.status_code}): {exc.response.text}"
            ) from exc

        token = response.text.strip()
        if not token:
            raise AuthenticationError("NiFi returned an empty token response")
        return token
