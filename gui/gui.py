# https://www.pythonguis.com/faq/pack-place-and-grid-in-tkinter/

import os
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import asksaveasfilename
from tkinter.colorchooser import askcolor
from tkinter.font import Font

from PIL import Image, ImageTk, ImageGrab

from choice import Choice
from constants import *
import imageProcessing


class Gui:
    root = Tk()

    def root_config(self):
        self.root.title("Image Editor")
        # self.master.maxsize(900, 900)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        w = 700
        h = 650
        x = (screen_width / 2) - (w / 2)
        y = (screen_height / 2) - (h / 2)

        self.root.geometry('%dx%d+%d+%d' % (w, h, x, 0))
        self.root.config(bg=BACKGROUND)  # , height=800, width=900

    def __init__(self):
        self.root_config()

        self.right_frame = Frame(self.root, bg='grey')
        self.right_frame.pack(side='right', fill='both', padx=10, pady=5, expand=True)

        self.canvas = Canvas(self.right_frame, bg='grey')
        self.canvas.pack(fill='both', padx=5, pady=5)
        self.canvas_setting()

        self.paint_setting_frame = Frame(self.right_frame, bg='lightgrey')
        self.paint_setting_frame.pack(fill='both', expand=1, padx=5, pady=5)

        self.left_frame = Frame(self.root, bg='grey')
        self.left_frame.pack(side='left', fill='both', padx=10, pady=5, expand=True)

        self.image = None
        self.img_path = None

        self.choice = Choice.NOTHING
        self.colors = ('red', 'blue')
        self.brush_width = StringVar(value=5)
        self.clear_width = StringVar(value=20)
        self.deleted_tag = "delete"  # this for the moving shape with the cursor (Paint && Clear)
        self.lines = []
        self.image_processing = imageProcessing.ImageProcessing()

        self.make_left_frame()

    # save && select
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

    def save2(self):
        if self.img_path is not None:
            ext = self.img_path.split(".")[-1]
            file = asksaveasfilename(defaultextension=f".{ext}", filetypes=[(
                "All Files", "*.*"), ("PNG file", "*.png"), ("jpg file", "*.jpg")])

            border_thickness_bd, highlight_thickness = 2, 1
            brdt = border_thickness_bd + highlight_thickness
            # +1 and -2 because of thicknesses of Canvas borders (bd-border and highlight-border):
            x = self.root.winfo_rootx() + self.right_frame.winfo_x() + self.canvas.winfo_x() + 1 * brdt
            y = self.root.winfo_rooty() + self.right_frame.winfo_y() + self.canvas.winfo_y() + 1 * brdt
            # x1 = x + self.canvas.winfo_width() - 2 * brdt
            # y1 = y + self.canvas.winfo_height() - 2 * brdt
            img = ImageTk.PhotoImage(self.image)
            x1 = x + img.width() - 2 * brdt
            y1 = y + img.height() - 2 * brdt
            ImageGrab.grab().crop((x, y, x1, y1)).save(file)

    # draw on canvas
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
        self.cursor_tracker(event)

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

    def choose(self, c):
        self.choice = c
        if self.image is not None:
            if self.choice == Choice.ROTATE:
                self.image = self.image_processing.rotate(self.image)
                self.put_image_in_canvas()  # do not put it out
            elif self.choice == Choice.TRANSLATE:
                self.image = self.image_processing.scale_rotate_translate(self.image, new_center=(100, 100))
                self.put_image_in_canvas()
            elif self.choice == Choice.SCALE:
                self.image = self.image_processing.resize(self.image)
                self.put_image_in_canvas()
            elif self.choice == Choice.SAVE:
                self.save2()
        if self.choice in (Choice.PAINT, Choice.CLEAR):
            self.put_paint_setting_frame()
        else:
            self.clear_paint_frame()

        if self.choice == Choice.SELECT:
            self.select()

    def put_image_in_canvas(self):
        self.canvas.delete("image")
        img = ImageTk.PhotoImage(self.image)
        # self.canvas.config(height=img.height(), width=img.width())
        self.canvas.create_image(0, 0, image=img, anchor='nw', tag="image")
        self.canvas.image = img

    def canvas_setting(self):
        self.canvas.bind("<Button-1>", self.get_x_and_y)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind('<Motion>', self.cursor_tracker)
        self.canvas.config(height=IMAGE_HIEGHT + 70, width=IMAGE_WIDTH - 70)

    def put_paint_setting_frame(self):
        if len(self.paint_setting_frame.winfo_children()) == 0:
            Button(self.paint_setting_frame, text='Select a Color', font="Times 15 roman normal",
                   command=self.change_color) \
                .pack(padx=5, pady=5)

            self.paint_width_frame(self.paint_setting_frame, "Change brush width", self.brush_width)
            self.paint_width_frame(self.paint_setting_frame, "Change clear width ", self.clear_width)

    def paint_width_frame(self, frame, text, textvarible):
        brush_width = Frame(frame, bg='lightgrey')
        brush_width.pack(fill='both', expand=1, padx=5, pady=5)

        Label(brush_width, text=text, bg='lightgrey', font="Times 18 roman normal") \
            .pack(side='left', padx=5, pady=5)

        Spinbox(brush_width, from_=0, to=30, width=3, textvariable=textvarible, wrap=True,
                font=Font(family='Times', size=25, weight='normal')).pack(side='left', padx=5, pady=5)

    def clear_paint_frame(self):
        for widgets in self.paint_setting_frame.winfo_children():
            widgets.destroy()

    def make_left_frame(self):
        img = Image.open("img.png")
        original_image = img.resize((100, 100))
        original_image = ImageTk.PhotoImage(original_image)

        tool_bar = Frame(self.left_frame, width=90, height=185, bg='lightgrey')
        tool_bar.pack(side='left', fill='both', padx=5, pady=5, expand=True)

        tool_bar2 = Frame(self.left_frame, width=90, height=185, bg='lightgrey')
        tool_bar2.pack(side='right', fill='both', padx=5, pady=5, expand=True)

        self.put_gesture(tool_bar, "Select", original_image, Choice.SELECT)
        self.put_gesture(tool_bar, "Rotate", original_image, Choice.ROTATE)
        self.put_gesture(tool_bar, "Scale", original_image, Choice.SCALE)
        self.put_gesture(tool_bar, "Translate", original_image, Choice.TRANSLATE)

        self.put_gesture(tool_bar2, "Save", original_image, Choice.SAVE)
        self.put_gesture(tool_bar2, "Warp", original_image, Choice.WARP)
        self.put_gesture(tool_bar2, "Clear", original_image, Choice.CLEAR)
        self.put_gesture(tool_bar2, "Paint", original_image, Choice.PAINT)

    def put_gesture(self, root, text, image, choice):
        Label(root, image=image).pack(fill='both', padx=5, pady=5)
        Button(root, text=text, command=lambda: self.choose(choice)).pack(padx=5, pady=5)


def main():
    Gui().root.mainloop()

    # print("quit")
    # root.quit()


if __name__ == '__main__':
    main()
