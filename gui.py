# https://www.pythonguis.com/faq/pack-place-and-grid-in-tkinter/

import os
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import asksaveasfilename
from tkinter.colorchooser import askcolor
from tkinter.font import Font

from PIL import Image, ImageTk, ImageGrab

from Queue import Queue
from choice import Choice
from constants import *
import imageProcessing
from hand_detection import *
from mouse import *
from finger_tracking import *


class Gui:
    root = Tk()

    def root_config(self):
        self.root.title("Image Editor")
        self.root.bind('s', self.s_press)
        self.root.bind('t', self.t_press)
        self.root.bind('z', self.z_press)

        # screen_width = self.root.winfo_screenwidth()
        # screen_height = self.root.winfo_screenheight()
        # print(screen_height, screen_width)
        x, y = 1366, 768
        self.root.geometry('%dx%d+%d+%d' % (x - 10, y - 70, 0, 0))
        self.root.config(bg=BACKGROUND1)

    def __init__(self):
        self.root_config()

        # video Frame
        self.video_frame = Frame(self.root, bg=BACKGROUND3)
        self.video_frame.pack(side='right', padx=5, pady=5)

        self.video_canvas = Canvas(self.video_frame, width=FRAME_WIDTH, height=FRAME_HEIGHT, bg=BACKGROUND1)
        self.video_canvas.pack(padx=5, pady=5)

        self.mask_drawing_frame = Frame(self.video_frame, bg=BACKGROUND3, width=FRAME_WIDTH, height=FRAME_HEIGHT)
        self.mask_drawing_frame.pack(padx=5, pady=5)

        self.mask_canvas = Canvas(self.mask_drawing_frame, width=FRAME_SMALL_WIDTH, height=FRAME_SMALL_HEIGHT,
                                  bg=BACKGROUND1)
        self.mask_canvas.pack(side='left', fill='both', expand=True, padx=5, pady=5)

        self.drawing_canvas = Canvas(self.mask_drawing_frame, width=FRAME_SMALL_WIDTH, height=FRAME_SMALL_HEIGHT,
                                     bg=BACKGROUND1)
        self.drawing_canvas.pack(side='right', fill='both', expand=True, padx=5, pady=5)

        self.cap = cv2.VideoCapture(0)

        # detection variables
        self.posture_queue = Queue(30, Choice.NOTHING)
        self.traverse_point = Queue(15)
        self.bgFrame = None
        self.frame = None
        self.enable = {
            "mouse": False,
            "tracking": False
        }
        self.get_new_frame()

        # image Frame
        self.image_frame = Frame(self.root, bg=BACKGROUND3, width=IMAGE_WIDTH)
        self.image_frame.pack(side='right', fill='both', padx=10, pady=5)

        self.canvas = Canvas(self.image_frame, bg=BACKGROUND3, height=IMAGE_HIEGHT, width=IMAGE_WIDTH)
        self.canvas.pack(fill='both', padx=5, pady=5)
        self.canvas_setting()

        self.paint_setting_frame = Frame(self.image_frame, bg=BACKGROUND2)
        self.paint_setting_frame.pack(fill='both', expand=1, padx=5, pady=5)

        # setting Frame
        self.setting_frame = Frame(self.root, bg=BACKGROUND3, width=300)
        self.setting_frame.pack(side='left', fill='both', padx=5, pady=5)
        self.make_left_frame()

        # gui variables
        self.image = None
        self.img_path = None

        self.choice = Choice.NOTHING
        self.colors = ('red', 'blue')
        self.brush_width = StringVar(value=5)
        self.clear_width = StringVar(value=20)
        self.deleted_tag = "delete"  # this for the moving shape with the cursor (Paint && Clear)
        self.lines = []
        self.image_processing = imageProcessing.ImageProcessing()

    # save && select
    def select(self):  # Load images from the computer
        self.img_path = filedialog.askopenfilename(initialdir=os.getcwd())
        if self.img_path is not None:
            self.image = Image.open(self.img_path)
            # print(self.image)
            self.image = self.image.resize((IMAGE_WIDTH, IMAGE_HIEGHT))
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
            x = self.root.winfo_rootx() + self.image_frame.winfo_x() + self.canvas.winfo_x() + brdt
            y = self.root.winfo_rooty() + self.image_frame.winfo_y() + self.canvas.winfo_y() + brdt
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

    def choose(self, c, value=None):
        self.choice = c
        if self.image is not None:
            if self.choice == Choice.ROTATE:
                self.image = self.image_processing.rotate(self.image,value if value else 180)
                self.put_image_in_canvas()  # do not put it out
            elif self.choice == Choice.TRANSLATE:
                self.image = self.image_processing.scale_rotate_translate(self.image, new_center=value if value else (80,80))  # tuple
                self.put_image_in_canvas()
            elif self.choice == Choice.SCALE:
                self.image = self.image_processing.resize(self.image,value if value else 0.8)
                self.put_image_in_canvas()
            elif self.choice == Choice.SAVE:
                self.save2()
            elif self.choice == Choice.SKEW:
                self.image = self.image_processing.shear(self.image,value if value else (0,130))
        if self.choice in (Choice.PAINT, Choice.CLEAR):
            self.put_paint_setting_frame()
        else:
            self.clear_paint_frame()

        if self.choice == Choice.SELECT:
            self.select()

    def put_image_in_canvas(self):
        self.canvas.delete("image")
        img = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=img, anchor='nw', tag="image")
        self.canvas.image = img

    def canvas_setting(self):
        self.canvas.bind("<Button-1>", self.get_x_and_y)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind('<Motion>', self.cursor_tracker)

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

        tool_bar = Frame(self.setting_frame, width=90, bg=BACKGROUND2)
        tool_bar.pack(side='left', fill='both', padx=5, pady=5, expand=True)

        tool_bar2 = Frame(self.setting_frame, width=90, bg=BACKGROUND2)
        tool_bar2.pack(side='left', fill='both', padx=2, pady=5, expand=True)

        tool_bar3 = Frame(self.setting_frame, width=90, bg=BACKGROUND2)
        tool_bar3.pack(side='right', fill='both', padx=5, pady=5, expand=True)

        self.put_gesture(tool_bar, "Select", original_image, Choice.SELECT)
        self.put_gesture(tool_bar, "Rotate", original_image, Choice.ROTATE)
        self.put_gesture(tool_bar, "Scale", original_image, Choice.SCALE)
        self.put_gesture(tool_bar, "Translate", original_image, Choice.TRANSLATE)

        self.put_gesture(tool_bar2, "Save", original_image, Choice.SAVE)
        self.put_gesture(tool_bar2, "Skew", original_image, Choice.SKEW)
        self.put_gesture(tool_bar2, "Clear", original_image, Choice.CLEAR)
        self.put_gesture(tool_bar2, "Paint", original_image, Choice.PAINT)

        self.put_gesture(tool_bar3, "Right", original_image, Choice.CLEAR)
        self.put_gesture(tool_bar3, "Left", original_image, Choice.PAINT)

    def put_gesture(self, root, text, image, choice):
        c = Canvas(root, width=100, height=100, bg=BACKGROUND1)
        c.pack(fill='both', padx=2, pady=5)
        c.create_image(0, 0, image=image, anchor='nw', tag="image")
        c.image = image
        Button(root, text=text, command=lambda: self.choose(choice)).pack(padx=5, pady=5)

    # video frame
    def s_press(self, s):
        self.enable["mouse"] = not self.enable["mouse"]

    def z_press(self, z):
        self.bgFrame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2YCrCb)

    def t_press(self, t):
        self.enable["tracking"] = not self.enable["tracking"]

    def get_new_frame(self):

        self.frame = self.cap.read()[1]
        self.frame = cv2.flip(self.frame, 1)
        drawing = np.zeros(self.frame.shape, np.uint8)

        try:
            skin_mask, contour, hull, center, defects = hand_detection(self.frame, self.bgFrame)
            s_mask = cv2.resize(skin_mask, (FRAME_SMALL_WIDTH, FRAME_SMALL_HEIGHT))
            self.show_frame(s_mask, self.mask_canvas)
            # cv2.imshow("skin", skin_mask)
            counter, is_space = count_fingers_spaces(defects['simplified'])

            res = detect_postures(self.frame, hull, contour, center,
                                  defects['simplified'])

            cv2.putText(self.frame, str(res), (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2, cv2.LINE_AA)

            cv2.drawContours(drawing, [contour, hull], -1, (0, 255, 0), 2)
            cv2.circle(self.frame, center, 5, [0, 0, 255], 2)
            for i, (start, end, far) in enumerate(defects['simplified']):
                cv2.line(self.frame, start, end, [0, 255, 0], 2)
                color = [255, 0, 0] if is_space[i] else [0, 0, 255]
                cv2.circle(self.frame, far, 5, color, -1)

            if self.enable["mouse"]:
                *s, _ = self.frame.shape
                move_mouse(get_highest_point(contour), s)

            if self.enable["tracking"]:
                tracking(self.frame, self.traverse_point, defects['original'], contour, center)
            # todo posture_quueue.append(posture)
            # choise = self.posture_queue.max_value()
            # value = self.traverse_point.first_last_diff()  # todo calculate this
            # gui.choose(choise, value)
        except Exception as e:
            print(e)
            pass

        drawing = cv2.resize(drawing, (FRAME_SMALL_WIDTH, FRAME_SMALL_HEIGHT))
        frm = cv2.resize(self.frame, (FRAME_WIDTH, FRAME_HEIGHT))
        self.show_frames((frm, self.video_canvas), (drawing, self.drawing_canvas))
        # Repeat after an interval to capture continiously
        self.video_canvas.after(5, self.get_new_frame)

    def show_frames(self, *frames):
        for frame, canvas in frames:
            self.show_frame(frame, canvas)

    def show_frame(self, frame, canvas):
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        canvas.imgtk = imgtk
        canvas.create_image(0, 0, image=imgtk, anchor='nw', tag="image")


def main():
    Gui().root.mainloop()
    # print("quit")
    # root.quit()


if __name__ == '__main__':
    main()
