from datetime import datetime

from colors import WHITE, RESET


def now(formatstr="%H:%M:%S") -> str:
    """Prints the time in a nice way"""
    return f"{WHITE}[{datetime.now().strftime(formatstr)}]{RESET}"
