from datetime import datetime

from colors import WHITE, RESET


def now(formatstr="%H:%M:%S") -> str:
    """Prints the time in a nice way"""
    return f"{WHITE}[{datetime.now().strftime(formatstr)}]{RESET}"

def now_usr(formatstr="%H:%M:%S", username:str=None) -> str:
    """Prints the time in a nice way"""
    if username:
        return f"{WHITE}[{datetime.now().strftime(formatstr)} {username}]{RESET}"
    else:
        return now(formatstr)

