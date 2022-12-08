import numpy as np
import cv2


def get_highest_point(contour):
    return min(contour, key=lambda c: c[0][1]).squeeze()

    # out = (float('inf'), float('inf'))
    # for c in contour:
    #     if out[1] > c[0][1]:
    #         out = c[0]

    # print(res, out)

    # return out


#
#
# def farthest_point(defects, contour, centroid):
#     out = None
#     if defects is not None and centroid is not None:
#
#         s = defects[:, 0][:, 0]
#
#         cx, cy = centroid
#
#         x = np.array(contour[s][:, 0][:, 0], dtype=np.float)
#         y = np.array(contour[s][:, 0][:, 1], dtype=np.float)
#
#         xp = cv2.pow(cv2.subtract(x, cx), 2)
#         yp = cv2.pow(cv2.subtract(y, cy), 2)
#         dist = cv2.sqrt(cv2.add(xp, yp))
#
#         dist_max_i = np.argmax(dist)
#
#         if dist_max_i < len(s):
#             farthest_defect = s[dist_max_i]
#             out = tuple(contour[farthest_defect][0])
#
#     return out
#

def draw_circles(frame, traverse_point):
    if traverse_point is not None:
        for i in range(len(traverse_point)):
            cv2.circle(frame, traverse_point[i], int(
                5 - (5 * i * 3) / 100), [0, 255, 255], -1)


def tracking(frame, traverse_point, defects, contour, centroid):
    far_point = get_highest_point(contour)
    if len(traverse_point) >= 20:
        traverse_point.pop(0)

    traverse_point.append(far_point)
    draw_circles(frame, traverse_point)
