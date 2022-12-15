
import numpy as np
import cv2
import math
import operator


def get_highest_point(contour):
    return min(contour, key=lambda c: c[0][1]).squeeze()


def get_lowest_point(contour):
    return max(contour, key=lambda c: c[0][1]).squeeze()


def get_leftmost_point(contour):
    return min(contour, key=lambda c: c[0][0]).squeeze()


def get_rightmost_point(contour):
    return max(contour, key=lambda c: c[0][0]).squeeze()


def dot_product(v1, v2):
    return sum(map(operator.mul, v1, v2))


def vector_cos(v1, v2):
    prod = dot_product(v1, v2)
    len1 = math.sqrt(dot_product(v1, v1))
    len2 = math.sqrt(dot_product(v2, v2))
    return prod / (len1 * len2)


def cnv2angle(x):
    return x/math.pi * 180


def cos_similarity(point, left, right, center) -> np.ndarray:
    cos = vector_cos(point - center, np.array([1, 0]))
    angle = math.acos(cos)
    if abs(cos) < 0.9:
        print(cnv2angle(math.acos(cos)))
        return point

    pc = point - center
    cos1 = vector_cos(pc, left - center)
    cos2 = vector_cos(pc, right - center)
    return left if cos1 > cos2 else right


print(cnv2angle(math.acos(0.9)))

kernel = np.ones((3, 3), np.uint8)


def closing(img):
    global kernel
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)


def opening(img):
    global kernel
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
