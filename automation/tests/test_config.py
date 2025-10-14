from nifi_automation.config import build_settings

def test_build_settings_overrides_env(monkeypatch):
    monkeypatch.setenv("NIFI_BASE_URL", "https://example.com/nifi-api")
    monkeypatch.setenv("NIFI_USERNAME", "env-user")
    monkeypatch.setenv("NIFI_PASSWORD", "env-pass")

    settings = build_settings(
        base_url="https://override.com/nifi-api",
        username="cli-user",
        password="cli-pass",
        verify_ssl=False,
        timeout=5.0,
    )

    assert settings.base_url == "https://override.com/nifi-api"
    assert settings.username == "cli-user"
    assert settings.password == "cli-pass"
    assert settings.verify_ssl is False
    assert settings.timeout == 5.0
