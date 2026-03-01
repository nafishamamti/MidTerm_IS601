import sys

from app.output_style import Fore, Style, OutputFormatter


def test_format_returns_plain_text_when_disabled():
    formatter = OutputFormatter(enable_colors=False)
    assert formatter.format("hello", "success") == "hello"


def test_format_returns_colored_text_when_enabled():
    formatter = OutputFormatter(enable_colors=True)
    assert formatter.format("hello", "success") == f"{Fore.GREEN}hello{Style.RESET_ALL}"


def test_format_unknown_style_returns_plain_text():
    formatter = OutputFormatter(enable_colors=True)
    assert formatter.format("hello", "unknown-style") == "hello"


def test_init_uses_env_and_tty(monkeypatch):
    monkeypatch.setenv("CALCULATOR_COLOR_OUTPUT", "true")
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    assert OutputFormatter().enable_colors is True


def test_init_honors_no_color(monkeypatch):
    monkeypatch.setenv("CALCULATOR_COLOR_OUTPUT", "true")
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    assert OutputFormatter().enable_colors is False
