# https://www.pythonguis.com/faq/pack-place-and-grid-in-tkinter/

import os
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import asksaveasfilename
from tkinter.colorchooser import askcolor
from PIL import Image, ImageTk

from choice import Choice
from constants import *
import imageProcessing


class Gui:
    root = Tk()

    def __init__(self):

        self.root.title("Image Editor")
        # self.master.maxsize(900, 900)
        self.root.config(bg="skyblue", height=900, width=900)

        self.right_frame = Frame(self.root, bg='grey')
        self.right_frame.pack(side='right', fill='both', padx=10, pady=5, expand=True)

        self.canvas = Canvas(self.right_frame, bg='grey')
        self.canvas.pack(fill='both', padx=5, pady=5)

        self.left_frame = Frame(self.root, bg='grey')
        self.left_frame.pack(side='left', fill='both', padx=10, pady=5, expand=True)

        self.image = None
        self.img_path = None

        self.choice = Choice.NOTHING
        self.colors = ('red', 'blue')
        self.brush_width = StringVar(value=2)
        self.clear_width = StringVar(value=20)
        self.deleted_tag = "delete"  # this for shape moving with the cursor
        self.lines = []
        self.image_processing = imageProcessing.ImageProcessing()

        self.make_left_frame()
        self.make_right_frame()
        print("hello")

    def get_x_and_y(self, event):
        global lasx, lasy
        lasx, lasy = event.x, event.y

    def draw(self, event):
        global lasx, lasy
        if self.choice == Choice.PAINT:
            w = int(self.brush_width.get())
            line = self.canvas.create_line((lasx, lasy, event.x, event.y), fill=self.colors[1], width=w)
            self.lines.append((line, lasx, lasy))

        elif self.choice == Choice.CLEAR:
            w = int(self.clear_width.get())
            for l in self.lines:
                (line, x, y) = l
                if (x - lasx) ** 2 + (lasy - y) ** 2 < w ** 2:
                    self.canvas.delete(line)
        lasx, lasy = event.x, event.y

    def cursor_tracker(self, e):
        x, y = e.x, e.y
        self.canvas.delete(self.deleted_tag)
        if self.choice == Choice.PAINT:
            self.canvas.create_rectangle((x, y, x, y), width=int(self.brush_width.get()), outline=self.colors[1],
                                         tag=self.deleted_tag)
        elif self.choice == Choice.CLEAR:
            w = int(self.clear_width.get())
            self.canvas.create_oval((x - w, y - w, x + w, y + w), outline="white", fill="", tag=self.deleted_tag)
        # print("Pointer is currently at %d, %d" % (x, y))

    def change_color(self):
        self.colors = askcolor(title="Tkinter Color Chooser")

    def clicked(self):
        '''if button is clicked, display message'''
        print("Clicked.")

    def choose(self, c):
        self.choice = c
        if self.choice == Choice.ROTATE:
            self.image = self.image_processing.rotate(self.image)
            self.put_image_in_canvas()  # do not put it out
        elif self.choice == Choice.TRANSLATE:
            self.image = self.image_processing.scale_rotate_translate(self.image, new_center=(100, 100))
            self.put_image_in_canvas()
        elif self.choice == Choice.SCALE:
            self.image = self.image_processing.resize(self.image)
            self.put_image_in_canvas()

    def select(self):  # Load images from the computer

        self.img_path = filedialog.askopenfilename(initialdir=os.getcwd())
        if self.img_path is not None:
            self.image = Image.open(self.img_path)
            print(self.image)
            self.image = self.image.resize((IMAGE_HIEGHT, IMAGE_WIDTH))
            self.put_image_in_canvas()

    def save(self):
        if self.img_path is not None:
            ext = self.img_path.split(".")[-1]
            file = asksaveasfilename(defaultextension=f".{ext}", filetypes=[(
                "All Files", "*.*"), ("PNG file", "*.png"), ("jpg file", "*.jpg")])
            self.image.save(file)

    def put_image_in_canvas(self):
        self.canvas.delete("image")
        img = ImageTk.PhotoImage(self.image)
        # self.canvas.config(height=img.height(), width=img.width())
        self.canvas.create_image(0, 0, image=img, anchor='nw', tag="image")
        self.canvas.image = img

    def make_right_frame(self):

        self.canvas.bind("<Button-1>", self.get_x_and_y)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind('<Motion>', self.cursor_tracker)

        # self.canvas.create_image(0, 0, image=self.image, anchor='nw')
        self.canvas.pack()
        self.canvas.config(height=IMAGE_HIEGHT + 70, width=IMAGE_WIDTH - 70)

        tool_bar3 = Frame(self.right_frame, bg='lightgrey')
        tool_bar3.pack(fill='both', expand=1, padx=5, pady=5)
        Button(tool_bar3, text='Select a Color', command=self.change_color).pack(padx=5, pady=5)
        # Button(tool_bar3, text=' Delete Line   ', command=self.delete_line).pack(padx=5, pady=5)
        Spinbox(tool_bar3, from_=0, to=30, textvariable=self.brush_width, wrap=True).pack(padx=5, pady=5)
        Spinbox(tool_bar3, from_=0, to=30, textvariable=self.clear_width, wrap=True).pack(padx=5, pady=5)

    def make_left_frame(self):
        img = Image.open("img.png")
        original_image = img.resize((100, 100))
        original_image = ImageTk.PhotoImage(original_image)

        tool_bar = Frame(self.left_frame, width=90, height=185, bg='lightgrey')
        tool_bar.pack(side='left', fill='both', padx=5, pady=5, expand=True)

        tool_bar2 = Frame(self.left_frame, width=90, height=185, bg='lightgrey')
        tool_bar2.pack(side='right', fill='both', padx=5, pady=5, expand=True)

        Label(tool_bar, image=original_image).pack(fill='both', padx=5, pady=5)
        Button(tool_bar, text="Select", command=self.select).pack(padx=5, pady=5)
        Label(tool_bar, image=original_image).pack(fill='both', padx=5, pady=5)
        Button(tool_bar, text="Rotate", command=lambda: self.choose(Choice.ROTATE)).pack(padx=5, pady=5)
        Label(tool_bar, image=original_image).pack(fill='both', padx=5, pady=5)
        Button(tool_bar, text="Scale", command=lambda: self.choose(Choice.SCALE)).pack(padx=5, pady=5)
        Label(tool_bar, image=original_image).pack(fill='both', padx=5, pady=5)
        Button(tool_bar, text="Translate", command=lambda: self.choose(Choice.TRANSLATE)).pack(padx=5, pady=5)

        Label(tool_bar2, image=original_image).pack(fill='both', padx=5, pady=5)
        Button(tool_bar2, text="Save", command=self.save).pack(padx=5, pady=5)
        Label(tool_bar2, image=original_image).pack(fill='both', padx=5, pady=5)
        Button(tool_bar2, text="Wrap", command=self.clicked).pack(padx=5, pady=5)
        Label(tool_bar2, image=original_image).pack(fill='both', padx=5, pady=5)
        Button(tool_bar2, text="Clear", command=lambda: self.choose(Choice.CLEAR)).pack(padx=5, pady=5)
        Label(tool_bar2, image=original_image).pack(fill='both', padx=5, pady=5)
        Button(tool_bar2, text="Paint", command=lambda: self.choose(Choice.PAINT)).pack(padx=5, pady=5)


def main():
    Gui().root.mainloop()

    # print("quit")
    # root.quit()


if __name__ == '__main__':
    main()
