from __future__ import annotations

from plainchange import portable
from plainchange.onboarding import OnboardingError


def test_portable_entry_uses_an_ephemeral_loopback_port(monkeypatch) -> None:
    captured = {}

    def fake_serve(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(portable, "serve_onboarding", fake_serve)

    assert portable.main() == 0
    assert captured == {"port": 0, "open_browser": True}


def test_portable_entry_surfaces_startup_failure_without_rethrowing(monkeypatch) -> None:
    shown = []

    def fail(**_kwargs):
        raise OnboardingError("Git is unavailable")

    monkeypatch.setattr(portable, "serve_onboarding", fail)
    monkeypatch.setattr(portable, "_show_startup_error", shown.append)

    assert portable.main() == 2
    assert shown == ["Git is unavailable"]
