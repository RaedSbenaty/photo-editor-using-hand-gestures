from enum import Enum
from Queue import Queue


class Directions(Enum):
    LEFT = -1 
    RIGHT = 1
    UP = 1
    DOWN = -1


def get_direction_from(q: Queue):
    start, end = q.q[0], q.q[-1]
    is_up = end[0] - start[0] < 0
    is_left = end[1] - start[1] < 0
    return (
        Directions.LEFT if is_left else Directions.RIGHT,
        Directions.UP if is_up else Directions.DOWN
    )

q = Queue(20)
q.append((10,10))
q.append((0,28))
print(get_direction_from(q))
