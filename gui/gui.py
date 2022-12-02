# https://www.pythonguis.com/faq/pack-place-and-grid-in-tkinter/

'''Example of how to use the pack() method to create a GUI layout'''
from tkinter import *
from PIL import Image, ImageTk
from tkinter.colorchooser import askcolor

from choice import Choice
from constants import *
import imageProcessing


class Gui():
    root = Tk()

    def __init__(self):

        self.root.title("Image Editor")
        # self.master.maxsize(900, 900)
        self.root.config(bg="skyblue", height=900, width=900)

        self.right_frame = Frame(self.root, width=650, height=800, bg='grey')
        self.right_frame.pack(side='right', fill='both', padx=10, pady=5, expand=True)

        self.canvas = Canvas(self.right_frame, bg='grey')
        self.canvas.pack(fill='both', expand=1, padx=5, pady=5)

        self.left_frame = Frame(self.root, width=200, height=600, bg='grey')
        self.left_frame.pack(side='left', fill='both', padx=10, pady=5, expand=True)

        img = Image.open("../img.png")
        img = img.resize((IMAGE_HIEGHT, IMAGE_HIEGHT))
        self.image = ImageTk.PhotoImage(img)

        self.choice = 0
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
        self.canvas.delete(self.deleted_tag)
        lasx, lasy = event.x, event.y

    def draw(self, event):
        global lasx, lasy
        w = int(self.brush_width.get())
        line = self.canvas.create_line((lasx, lasy, event.x, event.y), fill=self.colors[1], width=w)
        self.lines.append((line, lasx, lasy))
        lasx, lasy = event.x, event.y

    def callback(self, e):
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

    def delete_line(self):
        global lasx, lasy
        r = 50
        for l in self.lines:
            (line, x, y) = l
            if (x - lasx) ** 2 + (lasy - 100) ** 2 < r ** 2:
                print(line)
                self.canvas.delete(line)

    def clicked(self):
        '''if button is clicked, display message'''
        print("Clicked.")

    def choose(self, c):
        self.choice = c
        if self.choice == 1:
            self.image = self.image_processing.rotate()  # this should recieve path
        self.canvas.delete("image")
        self.canvas.create_image(0, 0, image=self.image, anchor='nw', tag="image")
        self.canvas.image = self.image

    def make_right_frame(self):

        self.canvas.bind("<Button-1>", self.get_x_and_y)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind('<Motion>', self.callback)

        self.canvas.create_image(0, 0, image=self.image, anchor='nw')
        self.canvas.pack()
        self.canvas.config(height=self.image.height(), width=self.image.width())

        tool_bar3 = Frame(self.right_frame, height=150, width=80, bg='lightgrey')
        tool_bar3.pack(fill='both', padx=5, pady=5)
        Button(tool_bar3, text='Select a Color', command=self.change_color).pack(padx=5, pady=5)
        Button(tool_bar3, text=' Delete Line   ', command=self.delete_line).pack(padx=5, pady=5)
        Spinbox(tool_bar3, from_=0, to=30, textvariable=self.brush_width, wrap=True).pack(padx=5, pady=5)

    def make_left_frame(self):
        img = Image.open("../img_1.png")
        original_image = img.resize((100, 100))
        original_image = ImageTk.PhotoImage(original_image)

        tool_bar = Frame(self.left_frame, width=90, height=185, bg='lightgrey')
        tool_bar.pack(side='left', fill='both', padx=5, pady=5, expand=True)

        tool_bar2 = Frame(self.left_frame, width=90, height=185, bg='lightgrey')
        tool_bar2.pack(side='right', fill='both', padx=5, pady=5, expand=True)

        Label(tool_bar, image=original_image).pack(fill='both', padx=5, pady=5)
        Button(tool_bar, text="Rotate", command=lambda: self.choose(1)).pack(padx=5, pady=5)
        Label(tool_bar, image=original_image).pack(fill='both', padx=5, pady=5)
        Button(tool_bar, text="Scale", command=self.clicked).pack(padx=5, pady=5)
        Label(tool_bar, image=original_image).pack(fill='both', padx=5, pady=5)
        Button(tool_bar, text="Translate", command=self.clicked).pack(padx=5, pady=5)

        Label(tool_bar2, image=original_image).pack(fill='both', padx=5, pady=5)
        Button(tool_bar2, text="Wrap", command=self.clicked).pack(padx=5, pady=5)
        Label(tool_bar2, image=original_image).pack(fill='both', padx=5, pady=5)
        Button(tool_bar2, text="Skew", command=self.clicked).pack(padx=5, pady=5)
        Label(tool_bar2, image=original_image).pack(fill='both', padx=5, pady=5)
        Button(tool_bar2, text="Paint", command=self.clicked).pack(padx=5, pady=5)


def main():
    Gui().root.mainloop()

    # print("quit")
    # root.quit()


if __name__ == '__main__':
    main()
