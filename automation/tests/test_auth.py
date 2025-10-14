import httpx
import pytest

from nifi_automation.auth import AuthenticationError, obtain_access_token
from nifi_automation.config import AuthSettings


class DummyResponse:
    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self.text = text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "error",
                request=httpx.Request("POST", "https://example.com"),
                response=httpx.Response(self.status_code, text=self.text),
            )


class DummyClient:
    def __init__(self, resp: DummyResponse):
        self.resp = resp

    def post(self, *_args, **_kwargs):
        return self.resp

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


class DummyClientFactory:
    def __init__(self, resp: DummyResponse):
        self.resp = resp

    def __call__(self, *args, **kwargs):
        return DummyClient(self.resp)


def test_obtain_access_token_success(monkeypatch):
    monkeypatch.setattr("nifi_automation.auth._client_factory", DummyClientFactory(DummyResponse(200, "token")))

    settings = AuthSettings(
        base_url="https://example.com/nifi-api",
        username="user",
        password="pass",
        verify_ssl=False,
        timeout=5.0,
    )
    assert obtain_access_token(settings) == "token"


def test_obtain_access_token_error(monkeypatch):
    monkeypatch.setattr("nifi_automation.auth._client_factory", DummyClientFactory(DummyResponse(401, "bad creds")))

    settings = AuthSettings(
        base_url="https://example.com/nifi-api",
        username="user",
        password="pass",
        verify_ssl=False,
        timeout=5.0,
    )

    with pytest.raises(AuthenticationError):
        obtain_access_token(settings)
