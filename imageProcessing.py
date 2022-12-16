import numpy as np
from PIL import Image, ImageTk
from numpy.linalg import inv

from constants import *
import math


class ImageProcessing:

    def rotate(self, img, rotation=180):
        return img.rotate(rotation)

    def scale_rotate_translate(self, image, angle=0, center=(0, 0), new_center=None, scale=None, expand=False):
        if center is None:
            return image.rotate(angle)
        angle = -angle / 180.0 * math.pi
        nx, ny = x, y = center
        sx = sy = 1.0
        if new_center:
            (nx, ny) = new_center
        if scale:
            (sx, sy) = scale
        cosine = math.cos(angle)
        sine = math.sin(angle)
        a = cosine / sx
        b = sine / sx
        c = x - nx * a - ny * b
        d = -sine / sy
        e = cosine / sy
        f = y - nx * d - ny * e
        # print(image.size)
        return image.transform((IMAGE_WIDTH, IMAGE_HIEGHT), Image.AFFINE, (a, b, c, d, e, f), resample=Image.BICUBIC)

    def scale(self, img, value):
        w, h = img.size
        img = img.resize((int(w * value), int(h * value)))
        return img

    def shear(self, img: Image, angles=(0, 0)) -> Image:
        x_angle, y_angle = angles
        w0, h0 = img.size
        angles = np.radians((x_angle, y_angle))
        tanx, tany = np.tan(angles)
        cosx, cosy = np.cos(angles)

        '''
        Transform the old image coordinates to the new image coordinates
        [ a b c ][ x ]   [ x']
        [ d e f ][ y ] = [ y']
        [ 0 0 1 ][ 1 ]   [ 1 ]
        '''
        shear = np.array((
            # x col    y col      global col
            (1 / cosx, tanx, max(0, -h0 * tanx)),  # -> x' row
            (tany, 1 / cosy, max(0, -w0 * tany)),  # -> y' row
            (0, 0, 1),  # -> 1  row
        ))

        size_transform = np.abs(shear[:2, :2])
        w1, h1 = (size_transform @ img.size).astype(int)

        print(shear)
        '''
        The original implementation was assigning old coordinates to new 
        coordinates on the left-hand side, so this needs to be inverted
        '''
        shear = inv(shear)
        print(shear)

        return img.transform(
            size=(w1, h1),
            method=Image.AFFINE,
            data=shear[:2, :].flatten(),
            # resample omitted - we don't really care about quality
        )



    # def shear(self, img: Image, angles=(0, 0)) -> Image:
    #     epsilon = 1e-12
    #     x_angle, y_angle = angles
    #     has_x, has_y = np.abs((x_angle, y_angle)) > epsilon
    #     if has_x and has_y:
    #         raise ValueError('Two-axis shear is not supported')
    #     if not (has_x or has_y):
    #         return img  # no-op
    #
    #     w0, h0 = img.size
    #     angles = np.radians((x_angle, y_angle))
    #     sinx, siny = np.sin(angles)
    #     cosx, cosy = np.cos(angles)
    #     tanx, tany = np.tan(angles)
    #
    #     '''
    #     Transform the old image coordinates to the new image coordinates
    #     [ a b c ][ x ]   [ x']
    #     [ d e f ][ y ] = [ y']
    #     [ 0 0 1 ][ 1 ]   [ 1 ]
    #     In the forward case (used for size transformation), the last row and last column are irrelevant.
    #     In the inverse case (used for image transformation), the last row is implied.
    #     '''
    #     shear_forward = np.array((
    #         (1 / cosx, tanx),
    #         (tany, 1 / cosy),
    #     ))
    #     shear_inverse = np.array((
    #         (cosx, -sinx, min(0, h0 * tanx) * cosx),
    #         (-siny, cosy, min(0, w0 * tany) * cosy),
    #     ))
    #     size_transform = np.abs(shear_forward)
    #     w1, h1 = (size_transform @ img.size).astype(int)
    #
    #     rhombised = img.transform(
    #         size=(w1, h1),
    #         method=Image.AFFINE,
    #         data=shear_inverse.flatten(),
    #         # resample omitted - we don't really care about quality
    #     )
    #
    #     return rhombised
