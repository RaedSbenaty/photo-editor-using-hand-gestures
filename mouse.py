import pyautogui
from motion_direction import Directions
import pyautogui as p


def convert(point, frame_size):
    sw, sh = pyautogui.size()
    fh, fw = frame_size
    rh, rw = sh / fh, sw / fw
    return point[0] * rw, point[1] * rh


def move_mouse2(point, frame_size):
    x, y = convert(point, frame_size)
    pyautogui.moveTo(x, y, 0.01, pyautogui.easeInQuad)


def smooth_scroll(value):
    for _ in range(5):
        pyautogui.scroll(value//5)


def scroll(direction: Directions):
    smooth_scroll(50*int(direction.value))


def click_state(state: Directions):
    if state is Directions.DOWN:
        pyautogui.mouseDown(button="left")
    elif state is Directions.UP:
        pyautogui.mouseUp(button="left")

def single_click(): # we can also call : click_state(Down) click_state(Up) to perform a click 
    pyautogui.click(button="left")
