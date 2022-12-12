from enum import Enum


class Choice(Enum):
    NOTHING = 0
    ROTATE = 1
    TRANSLATE = 2
    SCALE = 3
    WARP = 4
    SKEW = 5
    PAINT = 6
    CLEAR = 7
    SAVE = 8
    SELECT = 9
