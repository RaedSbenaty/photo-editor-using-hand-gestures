import pyautogui


def convert(point, frame_size):
    sw, sh = pyautogui.size()
    print(f"{sw=},{sh=}")
    fh, fw = frame_size
    rh, rw = sh / fh, sw / fw
    return point[0] * rw, point[1] * rh


# value = {
#     "old_x": None,
#     "old_y": None
# }


# def move_mouse(point, frame_size):
#     global value
#     old_x = value["old_x"]
#     old_y = value["old_y"]
#     if old_x is None:
#         old_x, old_y = convert(point, frame_size)
#     else:
#         new_x, new_y = convert(point, frame_size)
#         x, y = new_x - old_x, new_y - old_y
#         pyautogui.move(x, y)
#         old_x, old_y = new_x, new_y
#     value["old_x"] = old_x
#     value["old_y"] = old_y

def move_mouse2(point,frame_size):
    x,y = convert(point,frame_size)
    pyautogui.moveTo(x,y)
move_mouse2((500, 0), (1000, 1000))
move_mouse2((500, 500), (1000, 1000))
