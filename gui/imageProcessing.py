from PIL import Image, ImageTk

from constants import *
import math


class ImageProcessing:

    def rotate(self,  rotation=180):
        img = Image.open("../img.png")
        img = img.resize((IMAGE_HIEGHT, IMAGE_WIDTH))
        img = img.rotate(rotation)
        img = ImageTk.PhotoImage(img)
        return img
        # canvas.delete("image")
        # canvas.create_image(0, 0, image=img7, anchor='nw', tag="image")
        # canvas.image = img7

    def ScaleRotateTranslate(self, image, angle, center=None, new_center=None, scale=None, expand=False):
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
        return image.transform(image.size, Image.AFFINE, (a, b, c, d, e, f), resample=Image.BICUBIC)

    def update(self):
        img = Image.open("img.png")
        img = img.resize((380, 450))

        # img6 =  ScaleRotateTranslate(img,0, (0,0),(180,180))
        img7 = ImageTk.PhotoImage(img6)
        # canvas.delete("image")
        # canvas.create_image(0, 0, image=img7, anchor='nw', tag="image")
        # canvas.image = img7
