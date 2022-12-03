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


def ycbcr_substract(img1, img):
    diff = cv2.absdiff(img1, img)
    diff = diff[:, :, 1] + diff[:, :, 2]
    diff = (diff >= 10)*255
    return diff.astype(np.uint8)


def main():
    cap = cv2.VideoCapture(0)
    bgFrame = None

    while True:
        _, img = cap.read()
        skin_mask = generate_skin_mask(img)

        k = cv2.waitKey(30)
        if k & 0xff == 27:
            break

        elif k == ord('z') and bgFrame is None:
            bgFrame = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)

        elif bgFrame is not None:
            ycrcb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
            diff = ycbcr_substract(ycrcb_frame, bgFrame)
            final_result = diff & skin_mask
            cv2.imshow("ycbcr_substract", diff)
            cv2.imshow("skin_mask & ycbcr_substract", final_result)

        cv2.imshow('skin_mask', skin_mask)
        cv2.imshow('img', img)


if __name__ == '__main__':
    main()
