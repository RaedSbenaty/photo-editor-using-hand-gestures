from enum import Enum
from Queue import Queue


class Directions(Enum):
    LEFT = -1
    RIGHT = 1
    UP = 1
    DOWN = -1
    NO_DIR = 0


def get_direction_from(q: Queue):
    start, end = q.get_first_last()
    x_diff = end[1] - start[1]
    y_diff = end[0] - start[0]
    is_up = y_diff < 0
    is_left = x_diff < 0
    print(f"{x_diff=},{y_diff=}")
    out = [Directions.NO_DIR, Directions.NO_DIR]
    if abs(x_diff) > 10:
        out[0] = Directions.LEFT if is_left else Directions.RIGHT,
    if abs(y_diff) > 10:
        out[1] = Directions.UP if is_up else Directions.DOWN
    return out


q = Queue(20)
q.append((10, 10))
q.append((0, 28))
print(get_direction_from(q))
