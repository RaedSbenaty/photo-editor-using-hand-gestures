import numpy as np
from PIL import Image, ImageTk
from numpy.linalg import inv

from constants import *
import math


class ImageProcessing:

    def __init__(self):
        self.count_t = 0

    def watermark_with_transparency(self, img, watermark_image_path, position=(0, 0)):
        base_image = img.convert('RGBA')
        watermark = Image.open(watermark_image_path).convert('RGBA')
        width, height = base_image.size
        watermark = watermark.resize((width, height))
        watermark.putalpha(100)
        transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        transparent.paste(base_image, (0, 0))
        base_image.paste(watermark, position, mask=watermark)
        return base_image

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
            self.count_t += 1
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
        return image.transform((IMAGE_WIDTH * 2, IMAGE_HIEGHT * 2),
                               Image.AFFINE, (a, b, c, d, e, f), resample=Image.BICUBIC)

    def scale(self, img, value):
        w, h = img.size
        img = img.resize((int(w * value), int(h * value)))
        return img

    def shear(self, img: Image, angles=(0, 0)) -> Image:
        x_angle, y_angle = angles
        w0, h0 = img.size
        angles = np.radians((x_angle, int(y_angle)))
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

        '''
        The original implementation was assigning old coordinates to new 
        coordinates on the left-hand side, so this needs to be inverted
        '''
        shear = inv(shear)

        return img.transform(
            size=(w1, h1),
            method=Image.AFFINE,
            data=shear[:2, :].flatten(),
            # resample omitted - we don't really care about quality
        )
