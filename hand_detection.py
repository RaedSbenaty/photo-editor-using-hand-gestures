import cv2
import numpy as np
import math

kernel = np.ones((3, 3), np.uint8)


def opening(img):
    global kernel
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)


def generate_skin_mask(img):
    ycbcr = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    _, CR, CB = cv2.split(ycbcr)
    cb_6_cr = CB + 0.6*CR
    mask = (137 < CR) & (CR < 177) & (77 < CB) & (
        CB < 127) & (190 < cb_6_cr) & (cb_6_cr < 215)
    return mask.astype(np.uint8) * 255


def ycbcr_substract(img1, img):
    diff = cv2.absdiff(img1, img)
    diff = diff[:, :, 1] + diff[:, :, 2]
    diff = (diff >= 10)*255
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
    defects = cv2.convexityDefects(contour, hull)
    result = []

    if defects is not None:
        for i in range(defects.shape[0]):
            s, e, f, _ = defects[i, 0]
            result.append([tuple(contour[s][0]), tuple(
                contour[e][0]), tuple(contour[f][0])])

    return result


def hand_detection(frame, bgFrame=None):
    skin_mask = generate_skin_mask(frame)

    if bgFrame is not None:
        ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        diff = ycbcr_substract(ycrcb_frame, bgFrame)
        skin_mask = diff & skin_mask

    skin_mask = opening(skin_mask)
    contour = find_hand_contours(skin_mask)

    hull = cv2.convexHull(contour)
    center = find_center(contour)
    contour = cv2.approxPolyDP( contour, 0.01 * cv2.arcLength(contour, True), True)
    defects = find_defects(contour)

    return skin_mask, contour, hull, center, defects


def count_fingers_spaces(defects):
    counter = 0
    is_space = [False]*len(defects)

    for i, (start, end, far) in enumerate(defects):
        a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
        c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
        s = (a+b+c)/2

        ar = math.sqrt(s*(s-a)*(s-b)*(s-c))
        d = (2*ar)/a
        angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57

        if angle <= 90 and d > 30:
            is_space[i] = True
            counter += 1

    return counter, is_space
