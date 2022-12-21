# https://www.pythonguis.com/faq/pack-place-and-grid-in-tkinter/

import os
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import asksaveasfilename
from tkinter.colorchooser import askcolor
from tkinter.font import Font
import traceback
from PIL import Image, ImageTk, ImageGrab
from threading import Thread
from constants import *
import imageProcessing
from hand_detection import *
from mouse import *
from finger_tracking import *
from motion_direction import *
from input_mapper import *


class Gui:
    root = Tk()

    def root_config(self):
        self.root.title("Image Editor")
        self.root.bind('s', self.s_press)
        self.root.bind('t', self.t_press)
        self.root.bind('z', self.z_press)
        self.root.bind('b', self.b_press)
        self.root.bind('d', self.d_press)
        self.root.bind('o', self.o_press)
        self.root.bind('c', self.c_press)

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

        self.video_canvas = Canvas(
            self.video_frame, width=FRAME_WIDTH, height=FRAME_HEIGHT, bg=BACKGROUND1)
        self.video_canvas.pack(padx=5, pady=5)

        self.mask_drawing_frame = Frame(
            self.video_frame, bg=BACKGROUND3, width=FRAME_WIDTH, height=FRAME_HEIGHT)
        self.mask_drawing_frame.pack(padx=5, pady=5)

        self.mask_canvas = Canvas(self.mask_drawing_frame, width=FRAME_SMALL_WIDTH, height=FRAME_SMALL_HEIGHT,
                                  bg=BACKGROUND1)
        self.mask_canvas.pack(side='left', fill='both',
                              expand=True, padx=5, pady=5)

        self.drawing_canvas = Canvas(self.mask_drawing_frame, width=FRAME_SMALL_WIDTH, height=FRAME_SMALL_HEIGHT,
                                     bg=BACKGROUND1)
        self.drawing_canvas.pack(
            side='right', fill='both', expand=True, padx=5, pady=5)

        self.cap = cv2.VideoCapture(0)

        # detection variables
        self.is_selecting = False
        self.posture_queue = Queue(30, Choice.NOTHING)
        self.traverse_point = Queue(15, (0, 0))
        self.prev_bg_time = 0
        self.bgFrame = None
        self.frame = None
        self.frame_counter = 0
        self.input_mapper = Input_Mapper()
        self.enable = {
            "mouse": False,
            "tracking": False,
            "background": False,
            "choosing": False,
            "camera": False,
        }
        self.get_new_frame()

        # image Frame
        self.image_frame = Frame(self.root, bg=BACKGROUND3, width=IMAGE_WIDTH)
        self.image_frame.pack(side='right', fill='both', padx=10, pady=5)

        self.canvas = Canvas(self.image_frame, bg=BACKGROUND3,
                             height=IMAGE_HIEGHT, width=IMAGE_WIDTH)
        self.canvas.pack(fill='both', padx=5, pady=5)
        self.canvas_setting()

        self.paint_setting_frame = Frame(self.image_frame, bg=BACKGROUND2)
        self.paint_setting_frame.pack(fill='both', expand=1, padx=5, pady=5)

        # setting Frame
        self.setting_frame = Frame(self.root, bg=BACKGROUND3, width=300)
        self.setting_frame.pack(side='left', fill='both', padx=5, pady=5)
        self.setting_frame_widgets()

        # gui variables
        self.image = None
        self.images_prev = Queue(20)
        self.img_path = None

        self.choice = Choice.NOTHING
        self.colors = ('red', 'blue')
        self.brush_width = StringVar(value=5)
        self.clear_width = StringVar(value=20)
        # this for the moving shape with the cursor (Paint && Clear)
        self.deleted_tag = "delete"
        self.paint_tag = "paint"
        self.lines = []
        self.image_processing = imageProcessing.ImageProcessing()

        self.save_counter = 1

    def open_file_dialog(self):
        return filedialog.askopenfilename(
            initialdir=os.getcwd() + "/images")

    # save && select
    def select(self):  # Load images from the computer
        self.img_path = self.open_file_dialog()
        print("hello self,path", self.img_path)
        if self.img_path is not None and len(self.img_path) > 5:
            self.image = Image.open(self.img_path)
            # print(self.image)
            self.image = self.image.resize((IMAGE_WIDTH, IMAGE_HIEGHT))
            self.images_prev.append(self.image)
            self.images_prev.append(self.image)
            self.put_image_in_canvas()
        self.input_mapper.current_choice = Choice.NOTHING
        if self.enable['mouse']:
            self.s_press(None)
        self.is_selecting = False

    def save(self):
        if self.img_path is not None:
            ext = self.img_path.split(".")[-1]
            file = asksaveasfilename(defaultextension=f".{ext}", filetypes=[(
                "All Files", "*.*"), ("PNG file", "*.png"), ("jpg file", "*.jpg")])
            self.image.save(file)

    def save2(self):
        if self.img_path is not None:
            # ext = self.img_path.split(".")[-1]
            # file = asksaveasfilename(defaultextension=f".{ext}", filetypes=[(
            #     "All Files", "*.*"), ("PNG file", "*.png"), ("jpg file", "*.jpg")])

            file = f"images/save{self.save_counter}.png"
            self.save_counter += 1

            border_thickness_bd, highlight_thickness = 2, 1
            brdt = border_thickness_bd + highlight_thickness
            # +1 and -2 because of thicknesses of Canvas borders (bd-border and highlight-border):
            x = self.root.winfo_rootx() + self.image_frame.winfo_x() + \
                self.canvas.winfo_x() + brdt
            y = self.root.winfo_rooty() + self.image_frame.winfo_y() + \
                self.canvas.winfo_y() + brdt

            img = ImageTk.PhotoImage(self.image)
            width, height = (img.width(), img.height()) if IMAGE_WIDTH > img.width() else (
                IMAGE_WIDTH, IMAGE_HIEGHT)
            x1 = x + width - 2 * brdt
            y1 = y + height - 2 * brdt
            ImageGrab.grab().crop((x, y, x1, y1)).save(file)

    # draw on canvas
    def get_x_and_y(self, event):
        global lasx, lasy
        lasx, lasy = event.x, event.y

    def paint_line(self, x, y, x1, y1, w):
        return self.canvas.create_line(
            (x, y, x1, y1), fill=self.colors[1], width=w, tag=self.paint_tag)

    def paint_clear(self, event):
        global lasx, lasy
        if self.choice == Choice.PAINT:
            w = int(self.brush_width.get())
            line = self.paint_line(lasx, lasy, event.x, event.y, w)
            self.lines.append([line, lasx, lasy, event.x, event.y, w])
            print(lasx, lasy, event.x, event.y)
        elif self.choice == Choice.CLEAR:
            w = int(self.clear_width.get())
            for l in self.lines:
                (line, x, y, _, _, _) = l
                if (x - lasx) ** 2 + (lasy - y) ** 2 < w ** 2:
                    self.canvas.delete(line)
                    self.lines.remove(l)
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
            self.canvas.create_oval(
                (x - w, y - w, x + w, y + w), outline="white", fill="", tag=self.deleted_tag)
        # print("Pointer is currently at %d, %d" % (x, y))

    def change_color(self):
        self.colors = askcolor(title="Tkinter Color Chooser")
        self.is_selecting = False

    def add_water_mark_image(self):
        water_mark_path = self.open_file_dialog()
        if water_mark_path:
            self.image = self.image_processing.watermark_with_transparency(
                self.image, water_mark_path)
            self.put_image_in_canvas()
        self.is_selecting = False

    def choose(self, c, value=None):
        self.choice = c
        if value is not None:
            value = (int(value[0].value), int(value[1].value))
        # this for deleting cursor tracker
        self.canvas.delete(self.deleted_tag)
        if self.image is not None:
            if self.choice == Choice.UNDO:
                if self.images_prev.len() > 0:
                    prev = self.images_prev.pop()
                    if prev == 0:
                        self.canvas.delete(self.paint_tag)
                        self.lines = []
                    else:
                        self.image = prev
                        self.put_image_in_canvas()
                    if self.images_prev.len() == 0:  # to not fail in elif
                        self.images_prev.append(self.image.copy())
            elif self.choice not in (Choice.PAINT, Choice.CLEAR, Choice.SELECT, Choice.SAVE, Choice.NOTHING) and \
                    self.images_prev.q[-1] != self.image:
                self.images_prev.append(self.image.copy())
            elif self.choice == Choice.PAINT:
                self.images_prev.append(0)

            if self.choice == Choice.ROTATE:
                self.image = self.image_processing.rotate(
                    self.image, value[0] * 45 if value else 90)
                self.put_image_in_canvas()  # do not put it out
            elif self.choice == Choice.TRANSLATE:
                self.image = self.image_processing.scale_rotate_translate(self.image, new_center=(
                    value[0] * 30, value[1] * 30) if value else (40, 40))  # tuple
                self.put_image_in_canvas()
            elif self.choice == Choice.SCALE and value[0] is not Directions.NO_DIR:
                v = 1.2 if value[0] is Directions.LEFT else 0.8
                self.image = self.image_processing.scale(
                    self.image, v)
                self.put_image_in_canvas()
            elif self.choice == Choice.SAVE:
                self.save2()
                self.input_mapper.current_choice = Choice.NOTHING
            elif self.choice == Choice.SKEW:
                self.image = self.image_processing.shear(
                    self.image, (value[0] * 2, value[1]* 2) if value else (-1.5, 0.5))
                self.put_image_in_canvas()

            elif self.choice == Choice.WATER_MARK_IMAGE and not self.is_selecting:
                self.is_selecting = True
                Thread(target=self.add_water_mark_image).start()

        if self.choice in (Choice.PAINT, Choice.CLEAR):
            self.put_paint_setting_frame()
        elif self.input_mapper.current_choice == Choice.PAINT:
            if self.choice == Choice.SIZE_INC:
                self.brush_width.set(str(int(self.brush_width.get())+2))
            elif self.choice == Choice.SIZE_DEC:
                self.brush_width.set(str(int(self.brush_width.get())-2))
            elif self.choice == Choice.COLOR_PICKER and not self.is_selecting:
                self.is_selecting = True
                Thread(target=self.change_color).start()
        elif self.input_mapper.current_choice == Choice.CLEAR:
            if self.choice == Choice.SIZE_INC:
                self.clear_width += 2
            elif self.choice == Choice.SIZE_DEC:
                self.clear_width -= 2
        else:
            self.clear_paint_frame()

        if self.choice == Choice.SELECT and not self.is_selecting:
            self.canvas.delete(self.paint_tag)
            self.is_selecting = True
            Thread(target=self.select).start()

    def put_image_in_canvas(self):
        self.canvas.delete("image", self.paint_tag)
        img = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=img, anchor='nw', tag="image")
        self.canvas.image = img

        for l in self.lines:
            x, y, x1, y1, w = l[1:]
            line = self.paint_line(x, y, x1, y1, w)
            l[0] = line

    def canvas_setting(self):
        self.canvas.bind("<Button-1>", self.get_x_and_y)
        self.canvas.bind("<B1-Motion>", self.paint_clear)
        self.canvas.bind('<Motion>', self.cursor_tracker)

    def put_paint_setting_frame(self):
        if len(self.paint_setting_frame.winfo_children()) == 0:
            Button(self.paint_setting_frame, text='Select a Color', font="Times 15 roman normal",
                   command=self.change_color) \
                .pack(padx=5, pady=5)

            self.paint_width_frame(
                self.paint_setting_frame, "Change brush width", self.brush_width)
            self.paint_width_frame(
                self.paint_setting_frame, "Change clear width ", self.clear_width)

    def paint_width_frame(self, frame, text, text_variable):
        brush_width = Frame(frame, bg=BACKGROUND2)
        brush_width.pack(fill='both', expand=1, padx=5, pady=5)

        Label(brush_width, text=text, bg=BACKGROUND2, font="Times 18 roman normal") \
            .pack(side='left', padx=5, pady=5)

        Spinbox(brush_width, from_=0, to=30, width=3, textvariable=text_variable, wrap=True,
                font=Font(family='Times', size=25, weight='normal')).pack(side='left', padx=5, pady=5)

    def clear_paint_frame(self):
        for widgets in self.paint_setting_frame.winfo_children():
            widgets.destroy()

    def setting_frame_widgets(self):

        tool_bar = Frame(self.setting_frame, width=90, bg=BACKGROUND2)
        tool_bar.pack(side='left', fill='both', padx=5, pady=5, expand=True)

        tool_bar2 = Frame(self.setting_frame, width=90, bg=BACKGROUND2)
        tool_bar2.pack(side='left', fill='both', padx=2, pady=5, expand=True)

        tool_bar3 = Frame(self.setting_frame, width=90, bg=BACKGROUND2)
        tool_bar3.pack(side='right', fill='both', padx=5, pady=5, expand=True)

        self.put_gesture(tool_bar, "Select", Choice.SELECT)
        self.put_gesture(tool_bar, "Rotate", Choice.ROTATE)
        self.put_gesture(tool_bar, "Scale", Choice.SCALE)
        self.put_gesture(tool_bar, "Translate",
                         Choice.TRANSLATE)

        self.put_gesture(tool_bar2, "Save", Choice.SAVE)
        self.put_gesture(tool_bar2, "Skew", Choice.SKEW)
        self.put_gesture(tool_bar2, "Clear", Choice.CLEAR)
        self.put_gesture(tool_bar2, "Paint", Choice.PAINT)

        self.put_gesture(tool_bar3, "Water Mark", Choice.WATER_MARK_IMAGE)
        self.put_gesture(tool_bar3, "Undo", Choice.UNDO)
        # self.put_gesture(tool_bar3, "Right", Choice.CLEAR)
        # self.put_gesture(tool_bar3, "Left", Choice.PAINT)

    def put_gesture(self, root, text, choice):
        path = f"postures/{self.input_mapper.get_posture_of(choice).name}.PNG"
        print(path)
        img = Image.open(path)
        image = img.resize((100, 100))
        image = ImageTk.PhotoImage(image)

        c = Canvas(root, width=100, height=100, bg=BACKGROUND1)
        c.pack(fill='both', padx=2, pady=2)
        c.create_image(0, 0, image=image, anchor='nw', tag="image")
        c.image = image
        Button(root, text=text, command=lambda: self.choose(
            choice)).pack(padx=5, pady=5)

    # video frame
    def s_press(self, s):
        self.enable["mouse"] = not self.enable["mouse"]

    def z_press(self, z):
        self.bgFrame = cv2.cvtColor(self.orginal_frame, cv2.COLOR_BGR2YCrCb)
        # self.bgFrame = self.orginal_frame

    def t_press(self, t):
        self.enable["tracking"] = not self.enable["tracking"]

    def b_press(self, b):
        self.enable["background"] = not self.enable["background"]

    def d_press(self, d):
        self.root.destroy()

    def o_press(self, o):
        self.enable["choosing"] = not self.enable["choosing"]

    def c_press(self, c):
        self.enable["camera"] = not self.enable["camera"]

    def get_new_frame(self):

        if not self.enable["camera"]:
            # Repeat after an interval to capture continiously
            self.video_canvas.after(5, self.get_new_frame)
            return
        self.frame = self.cap.read()[1]
        self.frame = cv2.flip(self.frame, 1)
        self.orginal_frame = self.frame.copy()
        drawing = np.zeros(self.frame.shape, np.uint8)
        self.frame_counter += 1

        try:
            skin_mask, contour, hull, center, defects = hand_detection(
                self.frame, self.bgFrame)
            s_mask = cv2.resize(
                skin_mask, (FRAME_SMALL_WIDTH, FRAME_SMALL_HEIGHT))
            self.show_frame(s_mask, self.mask_canvas)

            if defects is not None:
                _, is_space = count_fingers_spaces(defects['simplified'])
                res = detect_postures(self.frame, hull, contour, center,
                                      defects['simplified'])

                self.posture_queue.append(res)
                highest_point = get_highest_point(contour)
                self.traverse_point.append(highest_point)
                cv2.putText(self.frame, str(self.posture_queue.max_value()._name_), (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 2, cv2.LINE_AA)
                cv2.putText(self.frame, str(self.input_mapper.current_choice._name_), (10, 100),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2, cv2.LINE_AA)
                if self.enable["choosing"]:
                    cv2.putText(self.frame, "Postures are Enabled", (300, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (255, 0, 0), 1, cv2.LINE_AA)
                cv2.drawContours(drawing, [contour], 0, [155, 100, 175], 2)
                cv2.drawContours(self.frame, [hull], 0, [0, 165, 255], 2)
                cv2.drawContours(drawing, [hull], 0, [0, 165, 255], 2)
                cv2.circle(self.frame, center, 5, [0, 0, 255], 2)

                for i, (_, _, far) in enumerate(defects['simplified']):
                    if is_space[i]:
                        cv2.circle(self.frame, far, 5, [255, 0, 0], -1)

                if self.enable["mouse"]:
                    *s, _ = self.frame.shape
                    move_mouse2(get_highest_point(contour), s)

                if self.enable["tracking"]:
                    tracking(self.frame, self.traverse_point,
                             defects['original'], contour, center)

                if self.frame_counter % 10 == 0 and self.enable["choosing"]:
                    posture = self.posture_queue.max_value()
                    choice = self.input_mapper.map(posture)
                    value = get_direction_from(self.traverse_point)
                    mouse_need_choices = [
                        Choice.SELECT, Choice.PAINT, Choice.COLOR_PICKER, Choice.CLEAR, Choice.CLICK, Choice.WATER_MARK_IMAGE]
                    # if choice need mouse and mouse is not enabled  ==> enable mouse
                    if choice in mouse_need_choices and not self.enable['mouse']:
                        self.enable['mouse'] = True
                        print(f"{self.enable['mouse']=}")
                    # else stop the mouse because there is no need to be enabled
                    else:
                        self.enable['mouse'] = False
                    print(f"{choice=},{value=}, {self.enable['mouse']=}")
                    # choice must not be click when the mouse is not enabled so the second condition must always be true  and self.enable['mouse']:
                    if choice is Choice.CLICK:
                        print("this is a click")
                        if self.input_mapper.current_choice in [Choice.PAINT, Choice.CLEAR]:
                            print("long click")
                            click_state(Directions.DOWN)
                        else:
                            print("double click")
                            double_click()
                    else:
                        print("else ")
                        click_state(Directions.UP)
                        if self.enable["choosing"]:
                            self.choose(choice, value)

        except:
            print('\n\n')
            traceback.print_exc()
            print('\n\n')

        drawing = cv2.resize(drawing, (FRAME_SMALL_WIDTH, FRAME_SMALL_HEIGHT))
        frm = cv2.resize(self.frame, (FRAME_WIDTH, FRAME_HEIGHT))
        self.show_frames((frm, self.video_canvas),
                         (drawing, self.drawing_canvas))
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
