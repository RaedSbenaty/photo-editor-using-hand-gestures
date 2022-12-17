import cv2
import numpy as np
import math

from posture import Posture
from utils import *

kernel = np.ones((3, 3), np.uint8)


def closing(img):
    global kernel
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)


def opening(img):
    global kernel
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)


def generate_skin_mask(img):
    ycbcr = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    _, CR, CB = cv2.split(ycbcr)
    cb_6_cr = CB + 0.6 * CR
    mask = (137 < CR) & (CR < 177) & (77 < CB) & (
        CB < 127) & (190 < cb_6_cr) & (cb_6_cr < 215)
    return mask.astype(np.uint8) * 255


# The color of the skin at unified daylight illumination
def generate_skin_mask2(img):
    B, G, R = cv2.split(img)
    mask = (R > 95) & (G > 40) & (B > 20) & (
        np.maximum(R, np.maximum(G, B)) - np.minimum(R, np.minimum(G, B)) > 15
    ) & (abs(R - G) > 15) & (R > G) & (R > B)
    return mask.astype(np.uint8) * 255


# The skin color under flashlight or (light) daylight lateral illumination
def generate_skin_mask3(img):
    B, G, R = cv2.split(img)
    mask = (R > 220) & (G > 210) & (B > 170) & (abs(
        R - G) <= 15) & (R > B) & (G > B)
    return mask.astype(np.uint8) * 255


def ycbcr_substract(img1, img):
    diff = cv2.absdiff(img1, img)
    diff = diff[:, :, 1] + diff[:, :, 2]
    diff = (diff >= 10) * 255
    return diff.astype(np.uint8)


def brg_substract(img1, img):
    diff = cv2.absdiff(img1, img)
    diff = diff[:, :, 0] + diff[:, :, 1] + diff[:, :, 2]
    diff = (diff >= 20) * 255
    return diff.astype(np.uint8)


def contour_filter(contour):
    width = get_rightmost_point(contour)[0] - get_leftmost_point(contour)[0]
    height = get_lowest_point(contour)[1] - get_highest_point(contour)[1]
    ratio = width/height
    return ratio > 0.4 and ratio < 1.7 and cv2.contourArea(contour) > 7000


def find_hand_contours(mask):
    contours, _ = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = list(filter(contour_filter, contours))
    if len(contours) == 0:
        return None

    result = max(contours, key=lambda c: cv2.contourArea(c))
    return result


def find_center(contour):
    moments = cv2.moments(contour)
    if moments['m00'] == 0:
        return None
    cx = int(moments['m10'] / moments['m00'])
    cy = int(moments['m01'] / moments['m00'])
    return (cx, cy)


def find_defects(contour):
    original_defects, simplified_defects = [], []

    hull = cv2.convexHull(contour, returnPoints=False)
    try:
        original_defects = cv2.convexityDefects(contour, hull)
    except:
        pass

    if original_defects is not None and len(original_defects) != 0:
        for i in range(original_defects.shape[0]):
            s, e, f, _ = original_defects[i, 0]
            simplified_defects.append([tuple(contour[s][0]), tuple(
                contour[e][0]), tuple(contour[f][0])])

    return {
        'original': original_defects,
        'simplified': simplified_defects
    }


# mini, maxi = float('inf'), -1


def hand_detection(frame, bgFrame=None):
    # global mini, maxi

    hull, defects, center = [None]*3
    skin_mask = generate_skin_mask2(frame)

    if bgFrame is not None:
        # ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        # diff = ycbcr_substract(ycrcb_frame, bgFrame)
        diff = brg_substract(frame, bgFrame)
        skin_mask = diff & skin_mask

    # skin_mask = opening(skin_mask)
    skin_mask = closing(skin_mask)
    contour = find_hand_contours(skin_mask)
    if contour is not None:
        hull = cv2.convexHull(contour)

        # k = cv2.waitKey(10)
        # if k == ord('h'):
        # width = get_rightmost_point(hull)[0] - get_leftmost_point(hull)[0]
        # height = get_lowest_point(hull)[1] - get_highest_point(hull)[1]
        # ratio = width/height
        # area = cv2.contourArea(hull)
        # mini = min(mini, width/height)
        # maxi = max(maxi, width/height)
        # print(mini, maxi)

        center = find_center(contour)
        contour = cv2.approxPolyDP(
            contour, 0.015 * cv2.arcLength(contour, True), True)
        defects = find_defects(contour)

    return skin_mask, contour, hull, center, defects


def count_fingers_spaces(defects):
    counter = len(defects) > 0
    is_space = [False] * len(defects)

    for i, (start, end, far) in enumerate(defects):
        a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
        c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
        s = (a + b + c) / 2

        ar = math.sqrt(s * (s - a) * (s - b) * (s - c))
        d = (2 * ar) / a
        angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

        if angle <= 90 and d > 30:
            is_space[i] = True
            counter += 1

    return counter, is_space


def detect_postures(frame, hull, contour, center, defects):
    finger_spaces_counter, is_space = count_fingers_spaces(defects)

    if finger_spaces_counter == 0:
        return Posture.ZERO

    center = np.array(center)
    left = get_leftmost_point(hull)
    right = get_rightmost_point(hull)
    up = get_highest_point(hull)
    down = get_lowest_point(hull)
    opened_defectes = [np.array(d[2]) for d, _ in filter(
        lambda s: s[1], zip(defects, is_space))]
    # cv2.circle(frame, right, 7, [0, 255, 255], 2)

    if finger_spaces_counter == 1:
        areahull = cv2.contourArea(hull)
        areacnt = cv2.contourArea(contour)
        return Posture.ONE_NORMAL if areacnt/areahull < 0.9 else Posture.ZERO

    if finger_spaces_counter == 2:
        nearest_point = cos_similarity(opened_defectes[0], left, right, center)
        if (nearest_point == opened_defectes[0]).all():
            return Posture.TWO_MIDDLE
        return Posture.TWO_LEFT if (nearest_point == right).all() else Posture.TWO_RIGHT

    if finger_spaces_counter == 3:
        if opened_defectes[0][0] < center[0] and opened_defectes[1][0] < center[0]:
            return Posture.THREE_RIGHT
        elif opened_defectes[0][0] > center[0] and opened_defectes[1][0] > center[0]:
            return Posture.THREE_LEFT
        else:
            return Posture.THREE_MIDDLE

    if finger_spaces_counter == 4:
        opened_defectes = sorted([d for d, _ in filter(
            lambda s: s[1], zip(defects, is_space))], key=lambda x: x[2][0])
        middle_defect = opened_defectes[1]
        start, end = middle_defect[0], middle_defect[1]
        # cv2.circle(frame, start, 7, [0, 255, 255], 2)
        return Posture.FOUR_RIGHT if start[1] > end[1] else Posture.FOUR_LEFT

    if finger_spaces_counter == 5:
        if sum([int(c[0] < center[0]) for c in opened_defectes]) >= 3:
            return Posture.FIVE_RIGHT_SIDE
        if sum([int(c[0] > center[0]) for c in opened_defectes]) >= 3:
            return Posture.FIVE_LEFT_SIDE
        lowest = max(opened_defectes, key=lambda c: c[1])
        return Posture.FIVE_RIGHT if lowest[0] < center[0] else Posture.FIVE_LEFT

    return Posture.NONE


# def detect_postures2(frame, hull, contour, finger_spaces_counter):
#     # define area of hull and area of hand
#     areahull = cv2.contourArea(hull)
#     areacnt = cv2.contourArea(contour)
#     # find the percentage of area not covered by hand in convex hull
#     arearatio = ((areahull - areacnt) / areacnt) * 100
#     # print corresponding gestures which are in their ranges
#     font = cv2.FONT_HERSHEY_SIMPLEX
#     if finger_spaces_counter == 1:
#         if areacnt < 2000:
#             cv2.putText(frame, 'Put hand in the box', (0, 50),
#                         font, 2, (0, 0, 255), 3, cv2.LINE_AA)
#         else:
#             if arearatio < 12:
#                 cv2.putText(frame, '0', (0, 50), font, 2,
#                             (0, 0, 255), 3, cv2.LINE_AA)
#             elif arearatio < 17.5:
#                 cv2.putText(frame, 'Best of luck', (0, 50),
#                             font, 2, (0, 0, 255), 3, cv2.LINE_AA)

#             else:
#                 cv2.putText(frame, '1', (0, 50), font, 2,
#                             (0, 0, 255), 3, cv2.LINE_AA)

#     elif finger_spaces_counter == 2:
#         cv2.putText(frame, '2', (0, 50), font, 2,
#                     (0, 0, 255), 3, cv2.LINE_AA)

#     elif finger_spaces_counter == 3:
#         if arearatio < 27:
#             cv2.putText(frame, '3', (0, 50), font, 2,
#                         (0, 0, 255), 3, cv2.LINE_AA)
#         else:
#             cv2.putText(frame, 'ok', (0, 50), font, 2,
#                         (0, 0, 255), 3, cv2.LINE_AA)

#     elif finger_spaces_counter == 4:
#         cv2.putText(frame, '4', (0, 50), font, 2,
#                     (0, 0, 255), 3, cv2.LINE_AA)

#     elif finger_spaces_counter == 5:
#         cv2.putText(frame, '5', (0, 50), font, 2,
#                     (0, 0, 255), 3, cv2.LINE_AA)

#     elif finger_spaces_counter == 6:
#         cv2.putText(frame, 'reposition', (0, 50), font,
#                     2, (0, 0, 255), 3, cv2.LINE_AA)

#     else:
#         cv2.putText(frame, 'reposition', (10, 50), font,
#                     2, (0, 0, 255), 3, cv2.LINE_AA)
