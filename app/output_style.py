import os
import sys
from typing import Dict

try:
    from colorama import Fore, Style, init
except ModuleNotFoundError:  # pragma: no cover
    class _NoColor:
        BLACK = "\033[30m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        WHITE = "\033[37m"
        RESET_ALL = "\033[0m"

    Fore = _NoColor()
    Style = _NoColor()

    def init(*_args, **_kwargs):
        return None

# Initialize Colorama once for cross-platform ANSI behavior.
init(autoreset=True)


class OutputFormatter:
    """Formats CLI output with optional ANSI colors."""

    _STYLE_COLORS: Dict[str, str] = {
        "info": Fore.CYAN,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
        "prompt": Fore.MAGENTA,
    }

    def __init__(self, enable_colors: bool | None = None):
        if enable_colors is None:
            color_env = os.getenv("CALCULATOR_COLOR_OUTPUT", "true").lower()
            allow_colors = color_env in {"1", "true", "yes", "on"}
            enable_colors = allow_colors and "NO_COLOR" not in os.environ and sys.stdout.isatty()
        self.enable_colors = enable_colors

    def format(self, text: str, style_name: str) -> str:
        """Return styled text when colors are enabled, else plain text."""
        if not self.enable_colors:
            return text
        color = self._STYLE_COLORS.get(style_name)
        if not color:
            return text
        return f"{color}{text}{Style.RESET_ALL}"
