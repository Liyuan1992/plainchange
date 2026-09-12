"""Windows portable entrypoint: open the local first-run page without a terminal."""

from __future__ import annotations

from .onboarding import OnboardingError, serve_onboarding


def _show_startup_error(message: str) -> None:
    try:
        import tkinter
        from tkinter import messagebox

        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        try:
            messagebox.showerror("PlainChange 无法启动", message)
        finally:
            root.destroy()
    except Exception:
        # A windowed portable executable has no reliable console. Do not make a
        # secondary UI failure mask the primary startup failure.
        return


def main() -> int:
    try:
        # An ephemeral port prevents an existing local development server from
        # making the double-click experience fail before the browser opens.
        serve_onboarding(port=0, open_browser=True)
    except (OnboardingError, OSError) as exc:
        _show_startup_error(str(exc))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
