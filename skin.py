import cv2
import numpy as np

kernel = np.ones((5, 5), np.uint8)


def opening(img):
    global kernel
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)


def closing(img):
    global kernel
    return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)


def generate_skin_mask(img):
    ycbcr = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    _, CR, CB = cv2.split(ycbcr)
    cb_6_cr = CB + 0.6*CR
    mask = (137 < CR) & (CR < 177) & (77 < CB) & (
        CB < 127) & (190 < cb_6_cr) & (cb_6_cr < 215)
    return mask.astype(np.uint8) * 255


def main():
    cap = cv2.VideoCapture(0)
    while True:
        _, img = cap.read()
        mask = generate_skin_mask(img)
        cv2.imshow('mask', mask)
        cv2.imshow('img', img)
        if cv2.waitKey(30) & 0xff == 27:
            break


if __name__ == '__main__':
    main()
