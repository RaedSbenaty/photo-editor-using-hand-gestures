from enum import Enum


class Choice(Enum):
    NOTHING = 0 #
    ROTATE = 1 #
    TRANSLATE = 2 #
    SCALE = 3 #
    SKEW = 5 #
    PAINT = 6 #
    CLEAR = 7 #
    SAVE = 8 #
    SELECT = 9 #
    CLICK = 10  #
    SIZE_INC = 11 #
    SIZE_DEC = 123
    COLOR_PICKER = 13 #
    UNDO = 14 #
    WATER_MARK_IMAGE = 15
    WAIT=16
