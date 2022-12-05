import cv2
import numpy as np
from hand_detection import hand_detection, count_fingers_spaces


def main():
    cap = cv2.VideoCapture(0)
    bgFrame = None

    while (cap.isOpened()):
        ret, frame = cap.read()
        drawing = np.zeros(frame.shape, np.uint8)

        k = cv2.waitKey(10)
        if k == ord('z'):
            print('background subtraction activated')
            bgFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        elif k & 0xff == 27:
            break

        try:
            skin_mask, contour, hull, center, defects = hand_detection(frame, bgFrame)
            counter, is_space = count_fingers_spaces(defects)
            # print(f'{counter=}')

            cv2.drawContours(drawing, [contour], 0, (0, 255, 0), 2)
            cv2.drawContours(drawing, [hull], 0, (255, 0, 255), 2)
            cv2.circle(frame, center, 5, [0, 0, 255], 2)

            for i, (start, end, far) in enumerate(defects):
                cv2.line(frame, start, end, [0, 255, 0], 2)
                color = [255, 0, 0] if is_space[i] else [0, 0, 255]
                cv2.circle(frame, far, 5, color, -1)

        except Exception as e:
            # print(e)
            pass

        cv2.imshow('input', frame)
        cv2.imshow('output', drawing)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
