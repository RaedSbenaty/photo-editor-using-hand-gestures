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


def ycbcr_substract(img1, img):
    diff = cv2.absdiff(img1, img)
    diff = diff[:, :, 1] + diff[:, :, 2]
    diff = (diff >= 10) * 255
    return diff.astype(np.uint8)


def find_hand_contours(mask):
    contours, _ = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return None
    return max(contours, key=lambda c: cv2.contourArea(c))


def find_center(contour):
    moments = cv2.moments(contour)
    if moments['m00'] == 0:
        return None
    cx = int(moments['m10'] / moments['m00'])
    cy = int(moments['m01'] / moments['m00'])
    return (cx, cy)


def find_defects(contour):
    hull = cv2.convexHull(contour, returnPoints=False)
    original_defects = cv2.convexityDefects(contour, hull)
    simplified_defects = []

    if original_defects is not None:
        for i in range(original_defects.shape[0]):
            s, e, f, _ = original_defects[i, 0]
            simplified_defects.append([tuple(contour[s][0]), tuple(
                contour[e][0]), tuple(contour[f][0])])

    return {
        'original': original_defects,
        'simplified': simplified_defects
    }


def hand_detection(frame, bgFrame=None):
    skin_mask = generate_skin_mask(frame)

    if bgFrame is not None:
        ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        diff = ycbcr_substract(ycrcb_frame, bgFrame)
        skin_mask = diff & skin_mask

    skin_mask = opening(skin_mask)
    # skin_mask = closing(skin_mask)
    contour = find_hand_contours(skin_mask)

    hull = cv2.convexHull(contour)
    center = find_center(contour)
    contour = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
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


def detect_postures(frame, hull, contour, finger_spaces_counter):
    # define area of hull and area of hand
    areahull = cv2.contourArea(hull)
    areacnt = cv2.contourArea(contour)
    # find the percentage of area not covered by hand in convex hull
    arearatio = ((areahull - areacnt) / areacnt) * 100
    # print corresponding gestures which are in their ranges
    font = cv2.FONT_HERSHEY_SIMPLEX
    if finger_spaces_counter == 1:
        if areacnt < 2000:
            cv2.putText(frame, 'Put hand in the box', (0, 50),
                        font, 2, (0, 0, 255), 3, cv2.LINE_AA)
        else:
            if arearatio < 12:
                cv2.putText(frame, '0', (0, 50), font, 2,
                            (0, 0, 255), 3, cv2.LINE_AA)
            elif arearatio < 17.5:
                cv2.putText(frame, 'Best of luck', (0, 50),
                            font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            else:
                cv2.putText(frame, '1', (0, 50), font, 2,
                            (0, 0, 255), 3, cv2.LINE_AA)

    elif finger_spaces_counter == 2:
        cv2.putText(frame, '2', (0, 50), font, 2,
                    (0, 0, 255), 3, cv2.LINE_AA)

    elif finger_spaces_counter == 3:
        if arearatio < 27:
            cv2.putText(frame, '3', (0, 50), font, 2,
                        (0, 0, 255), 3, cv2.LINE_AA)
        else:
            cv2.putText(frame, 'ok', (0, 50), font, 2,
                        (0, 0, 255), 3, cv2.LINE_AA)

    elif finger_spaces_counter == 4:
        cv2.putText(frame, '4', (0, 50), font, 2,
                    (0, 0, 255), 3, cv2.LINE_AA)

    elif finger_spaces_counter == 5:
        cv2.putText(frame, '5', (0, 50), font, 2,
                    (0, 0, 255), 3, cv2.LINE_AA)

    elif finger_spaces_counter == 6:
        cv2.putText(frame, 'reposition', (0, 50), font,
                    2, (0, 0, 255), 3, cv2.LINE_AA)

    else:
        cv2.putText(frame, 'reposition', (10, 50), font,
                    2, (0, 0, 255), 3, cv2.LINE_AA)


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
        arearatio = ((areahull - areacnt) / areacnt) * 100
        # if arearatio < 17.5:
        #     return Posture.ONE_OK

        return Posture.ONE_NORMAL

    if finger_spaces_counter == 2:
        nearest_point = cos_similarity(opened_defectes[0], left, right, center)
        if (nearest_point == opened_defectes[0]).all():
            return Posture.TWO_MIDDLE
        return Posture.TWO_LEFT if (nearest_point == right).all() else Posture.TWO_RIGHT

        # distance_to_left = abs(opened_defectes[0][0]-left[0])
        # distance_to_right = abs(opened_defectes[0][0]-right[0])
        # distance_to_center = abs(opened_defectes[0][0]-center[0])

        # mini = min(distance_to_left, distance_to_right, distance_to_center)

        # if mini == distance_to_left:
        #     return Posture.TWO_LEFT
        # if mini == distance_to_right:
        #     return Posture.TWO_RIGHT
        # else:
        #     return Posture.TWO_MIDDLE

    if finger_spaces_counter == 3:
        if opened_defectes[0][0] < center[0] and opened_defectes[1][0] < center[0]:
            return Posture.THREE_LEFT
        elif opened_defectes[0][0] > center[0] and opened_defectes[1][0] > center[0]:
            return Posture.THREE_RIGHT
        else:
            return Posture.THREE_MIDDLE

    if finger_spaces_counter == 4:
        return Posture.FOUR

    if finger_spaces_counter == 5:
        if sum([int(c[0] < center[0]) for c in opened_defectes]) >= 3:
            return Posture.FIVE_RIGHT_SIDE
        if sum([int(c[0] > center[0]) for c in opened_defectes]) >= 3:
            return Posture.FIVE_LEFT_SIDE
        lowest = max(opened_defectes, key=lambda c: c[1])
        return Posture.FIVE_RIGHT if lowest[0] < center[0] else Posture.FIVE_LEFT
