from enum import Enum
from Queue import Queue


class Directions(Enum):
    LEFT = -1
    RIGHT = 1
    UP = -1.1
    DOWN = 1.1
    NO_DIR = 0


def get_direction_from(q: Queue):
    x_diff,y_diff = get_diff(q)
    x_diff, y_diff = y_diff,x_diff
    is_up = y_diff < 0
    is_left = x_diff < 0
    out = [Directions.NO_DIR, Directions.NO_DIR]
    if abs(x_diff) > 30:
        out[0] = Directions.LEFT if is_left else Directions.RIGHT
    if abs(y_diff) > 30:
        out[1] = Directions.UP if is_up else Directions.DOWN
    return out

def get_diff(q:Queue):
    start, end = q.get_first_last()
    x_diff = end[1] - start[1]
    y_diff = end[0] - start[0]
    if abs(x_diff) < 50:
        x_diff = 0 
    if abs(y_diff) < 50:
        y_diff = 0 
    return x_diff,y_diff
