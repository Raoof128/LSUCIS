from importlib import reload

import utils.secrets as secrets


def test_cli_key_precedence(monkeypatch):
    monkeypatch.setenv("SATCOM_KEY", "ENVVALUE")
    key, used_demo = secrets.resolve_hmac_key("CLIKEY")
    assert key == b"CLIKEY"
    assert used_demo is False


def test_environment_fallback(monkeypatch):
    monkeypatch.setenv("SATCOM_KEY", "ENVVALUE")
    key, used_demo = secrets.resolve_hmac_key(None)
    assert key == b"ENVVALUE"
    assert used_demo is False


def test_demo_fallback(monkeypatch):
    monkeypatch.delenv("SATCOM_KEY", raising=False)
    key, used_demo = secrets.resolve_hmac_key(None)
    assert key == secrets.DEMO_KEY
    assert used_demo is True


def test_no_fallback_raises(monkeypatch):
    monkeypatch.delenv("SATCOM_KEY", raising=False)
    # Ensure reload resets any state
    reload(secrets)
    try:
        secrets.resolve_hmac_key(None, allow_demo_fallback=False)
    except ValueError as exc:
        assert "HMAC key not provided" in str(exc)
    else:
        raise AssertionError("Expected ValueError when no key is provided")
