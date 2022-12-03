from PIL import Image, ImageTk

from constants import *
import math


class ImageProcessing:

    def rotate(self, img, rotation=180):
        return img.rotate(rotation)

    def scale_rotate_translate(self, image, angle=0, center=(0,0), new_center=None, scale=None, expand=False):
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
        return image.transform((IMAGE_HIEGHT,IMAGE_WIDTH), Image.AFFINE, (a, b, c, d, e, f), resample=Image.BICUBIC)

    def resize(self,img):
        img = img.resize((200, 200))
        return img
