from threading import Thread

from choice import Choice
from gui import Gui
from hand_detection import *
from mouse import *
from finger_tracking import *
from Queue import *

def main():
    # gui = Gui()
    # gui_root = gui.root
    # Thread(target = gui_root.mainloop).start()
    posture_queue = Queue(30,Choice.NOTHING)
    traverse_point = Queue(30)
    cap = cv2.VideoCapture(0)
    bgFrame = None
    enable = {
        "mouse": False,
        "tracking": False
    }
    
    while (cap.isOpened()):
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        drawing = np.zeros(frame.shape, np.uint8)

        k = cv2.waitKey(10)
        if k == ord('z'):
            bgFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        elif k == ord('s'):
            enable["mouse"] = not enable["mouse"]
        elif k == ord('t'):
            enable["tracking"] = not enable["tracking"]
        elif k & 0xff == 27:
            break
        
        try:
            skin_mask, contour, hull, center, defects = hand_detection(frame, bgFrame)
            cv2.imshow('skin', skin_mask)
            counter, is_space = count_fingers_spaces(defects['simplified'])
            
            # print(f'{counter=}')
            # detect_postures(frame, hull, contour, counter)

            cv2.drawContours(drawing, [contour, hull], -1, (0, 255, 0), 2)
            cv2.circle(frame, center, 5, [0, 0, 255], 2)
            for i, (start, end, far) in enumerate(defects['simplified']):
                cv2.line(frame, start, end, [0, 255, 0], 2)
                color = [255, 0, 0] if is_space[i] else [0, 0, 255]
                cv2.circle(frame, far, 5, color, -1)
                
            if enable["mouse"]:
                *s, _ = frame.shape
                move_mouse(center, s)
                
            if enable["tracking"]:
                tracking(frame, traverse_point, defects['original'] , contour, center)
         # todo posture_quueue.append(posture)
            choise = posture_queue.max_value()
            value = traverse_point.first_last_diff()# todo calculate this
            # gui.choose(choise,value )
        except Exception as e:
            print(e)
            pass

        cv2.imshow('input', frame)
        cv2.imshow('output', drawing)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
