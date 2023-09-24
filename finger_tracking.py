import numpy as np
import cv2
from utils import get_highest_point

def draw_circles(frame, traverse_point):
    for i in range(len(traverse_point.q)):
        cv2.circle(frame, traverse_point.q[i], int(
            5 - (5 * i * 3) / 100), [0, 255, 255], -1)


def tracking(frame, traverse_point, defects, contour, centroid):
    far_point = get_highest_point(contour)
    traverse_point.append(far_point)
    draw_circles(frame, traverse_point)
