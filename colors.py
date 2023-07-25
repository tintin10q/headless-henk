#!/usr/bin/env python3
# https://github.com/tintin10q/python-colors/blob/main/colors.py
# wget https://raw.githubusercontent.com/tintin10q/python-colors/main/colors.py

import os

__author__ = 'Quinten Cabo'
__license__ = 'GNU 2'


def supports_color() -> bool:
    """
    Returns True if the running system's terminal supports color, and False
    otherwise.
    """
    import sys
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    return supported_platform and is_a_tty


def clear_console():
    """ Runs the console clear command in a simple platform specific way """
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


STOP = ''

BOLD = ''
FAINT = ''
ITALICS = ''
UNDERLINE = ''

BLINK = ''
RAPID_BLINK = ''

INVERT = ''
HIDE = ''

STRIKE = ''

FONT0 = ''  # Font 0 is the default
FONT1 = ''
FONT2 = ''
FONT3 = ''
FONT4 = ''
FONT5 = ''
FONT6 = ''
FONT7 = ''
FONT8 = ''
FONT9 = ''

Fraktur = ''  # This one is rarely supported

DOUBLEUNDERLINE = ''

STOP_INTENSITY = ''
STOP_ITALICBOLD = ''
STOP_BLINK = ''

STOP_UNDERLINE = ''
STOP_REVERSE = ''
STOP_HIDE = ''
STOP_STIKE = ''

PROPORTIONAL_SPACING = ''
STOP_PROPORTIONAL_SPACING = ''

FRAME = ''  # Not supported often
ENCIRCLE = ''
OVERLINE = ''  # Often not supported aswell
STOP_FRAME_ENCIRCLE = ''
STOP_OVERLINE = ''

BLACK = ''
RED = ''
GREEN = ''
YELLOW = ''
BLUE = ''
AQUA = ''
PURPLE = ''
AQUA = ''
WHITE = ''

BLACK_BG = ''
RED_BG = ''
GREEN_BG = ''
YELLOW_BG = ''
AQUA_BG = ''
PURPLE_BG = ''
AQUA_BG = ''
WHITE_BG = ''

LIGHTBLACK = ''
LIGHTRED = ''
LIGHTGREEN = ''
LIGHTYELLOW = ''
LIGHTAQUA = ''
LIGHTPURPLE = ''
LIGHTAQUA = ''
LIGHTWHITE = ''

LIGHTBLACK_BG = ''
LIGHTRED_BG = ''
LIGHTGREEN_BG = ''
LIGHTYELLOW_BG = ''
LIGHTAQUA_BG = ''
LIGHTPURPLE_BG = ''
LIGHTAQUA_BG = ''
LIGHTWHITE_BG = ''

BELL = BEEP = '\a'  # This makes a sound when you print it

SUPERSCRIPT = ''  # Only on mintty All 3 of these
SUBSCRIPT = ''
STOP_SUPERSUBSCRIPT = ''

CLEAR = '\033c'  # Clear the screen

if supports_color():
    STOP = '\033[0m'  # No Color

    BOLD = '\033[1m'
    FAINT = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'

    BLINK = '\033[5m'
    RAPID_BLINK = '\033[6m'  # More than 150 times a minute not widly supported

    INVERT = '\033[7m'  # INVERT BG and TEXT not widly supported
    HIDE = '\033[8m'  # Not widly supported, don't rely on it.
    STRIKE = '\033[9m'  # Not widly supported, don't rely on it.

    FONT0 = '\033[10m'  # Font 0 is the default
    FONT1 = '\033[11m'
    FONT2 = '\033[12m'
    FONT3 = '\033[13m'
    FONT4 = '\033[14m'
    FONT5 = '\033[15m'
    FONT6 = '\033[16m'
    FONT7 = '\033[17m'
    FONT8 = '\033[18m'
    FONT9 = '\033[19m'

    Fraktur = '\033[19m'  # This one is rarely supported

    DOUBLEUNDERLINE = '\033[21m'  # Also non bold in some terminals
    STOP_INTENSITY = '\033[22m'
    STOP_ITALICBOLD = '\033[23m'

    STOP_UNDERLINE = '\033[24m'
    STOP_BLINK = '\033[25m'

    PROPORTIONAL_SPACING = '\033[26m'  # Not supported often

    STOP_REVERSE = '\033[27m'
    STOP_HIDE = '\033[28m'
    STOP_STIKE = '\033[29m'

    STOP_PROPORTIONAL_SPACING = '\033[50m'  # Not supported often

    FRAME = '\033[51m'  # Not supported often
    ENCIRCLE = '\033[52m'
    OVERLINE = '\033[53m'  # Often not supported aswell
    STOP_FRAME_ENCIRCLE = '\033[54m'
    STOP_OVERLINE = '\033[55m'

    BLACK = '\033[0;30m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    AQUA = '\033[0;36m'
    WHITE = '\033[0;37m'

    BLACK_BG = '\033[0;40m'
    RED_BG = '\033[0;41m'
    GREEN_BG = '\033[0;42m'
    YELLOW_BG = '\033[0;43m'
    AQUA_BG = '\033[0;44m'
    PURPLE_BG = '\033[0;45m'
    AQUA_BG = '\033[0;46m'
    WHITE_BG = '\033[0;47m'

    LIGHTBLACK = '\033[0;90m'
    LIGHTRED = '\033[0;91m'
    LIGHTGREEN = '\033[0;92m'
    LIGHTYELLOW = '\033[0;93m'
    LIGHTAQUA = '\033[0;94m'
    LIGHTPURPLE = '\033[0;95m'
    LIGHTAQUA = '\033[0;96m'
    LIGHTWHITE = '\033[0;97m'

    LIGHTBLACK_BG = '\033[0;100m'
    LIGHTRED_BG = '\033[0;101m'
    LIGHTGREEN_BG = '\033[0;102m'
    LIGHTYELLOW_BG = '\033[0;103m'
    LIGHTAQUA_BG = '\033[0;104m'
    LIGHTPURPLE_BG = '\033[0;105m'
    LIGHTAQUA_BG = '\033[0;106m'
    LIGHTWHITE_BG = '\033[0;107m'

    SUPERSCRIPT = '\033[73m'  # Only on mintyy all 3 of these
    SUBSCRIPT = '\033[74m'
    STOP_SUPERSUBSCRIPT = '\033[75m'

# Aliases
NORMAL = RESET = STOP
SLOW_BLINK = BLINK  # Less than 150 times a minute
DIM = FAINT

BLINK_SLOW = SLOW_BLINK
BLINK_RAPID = RAPID_BLINK

CONCEAL = SPOILER = HIDE

CROSSOUT = STRIKE
STOP_CROSSOUT = STOP_STIKE

REVEAL = STOP_HIDE

R = RESET


def printc(*args: object, STOPPER: object = STOP, **kwargs: object, ) -> object:
    """Automatically puts a color stop sign at the end of the print """
    print(*args, **kwargs, end=STOPPER + '\n')


# It is also a good idea to set sep when printing because then you can just use the commas. Otherwise, use +.


def show_table(up_to=110):
    """ Shows table of colors, so you can see what numbers you can use. """
    STOP = '\033[0m'  # No Color
    for i in range(up_to):
        print(f'\033[0;{i}m', i, end=f'{STOP} ')
    printc()


def printgreen(*args, **kwargs):
    printc(GREEN, *args, **kwargs)

if __name__ == '__main__':
    from sys import argv

    STOP = '\033[0m'  

    up_to = 110

    if len(argv) > 1 and argv[1].isnumeric():  # You can pass the number to print to as an arg
        up_to = int(argv[1]) + 1  # Plus one so that if you type 20 you actually get 20
    up_to += 1
    print(up_to)
    show_table(up_to)