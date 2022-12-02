# https://www.pythonguis.com/faq/pack-place-and-grid-in-tkinter/

'''Example of how to use the pack() method to create a GUI layout'''
from tkinter import *
from PIL import Image, ImageTk
from tkinter.colorchooser import askcolor

root = Tk()  # create root window
root.title("Basic GUI Layout with Pack")
root.maxsize(900, 900)
root.config(bg="skyblue")

colors = ('red', 'blue')
width = StringVar(value=2)
clear_width = StringVar(value=20)
deleted_tag = "delete"
lines = [(0, 0, 0)]


def get_x_and_y(event):
    global lasx, lasy
    canvas.delete(deleted_tag)
    lasx, lasy = event.x, event.y


def draw_smth(event):
    global lasx, lasy
    global lines
    line = canvas.create_line((lasx, lasy, event.x, event.y), fill=colors[1], width=int(width.get()))
    lines.append((line, lasx, lasy))
    # print(len(lines),lasx,lasy,lines[-1])
    # print(width)
    lasx, lasy = event.x, event.y


def callback(e):
    x = e.x
    y = e.y
    canvas.delete(deleted_tag)
    # canvas.after(100,)
    # canvas.create_rectangle((x,y,x,y), width=int(width.get()),outline=colors[1],tag = deleted_tag)
    w = int(clear_width.get())

    canvas.create_oval((x - w, y - w, x + w, y + w), outline="white", fill="", tag=deleted_tag)
    # print("Pointer is currently at %d, %d" % (x, y))


def change_color():
    global colors
    colors = askcolor(title="Tkinter Color Chooser")
    # root.configure(bg=colors[1])


def delete_line():
    x, y = 100, 100
    r = 50
    for l in lines:
        (line, x, y) = l
        if (x - 100) ** 2 + (y - 100) ** 2 < r ** 2:
            print(line)
            canvas.delete(line)


# Create left and right frames
left_frame = Frame(root, width=200, height=600, bg='grey')
left_frame.pack(side='left', fill='both', padx=10, pady=5, expand=True)

right_frame = Frame(root, width=650, height=800, bg='grey')
right_frame.pack(side='right', fill='both', padx=10, pady=5, expand=True)

# Create frames and labels in left_frame
# Label(left_frame,  text="Original Image").pack(side='top',  padx=5,  pady=5)
image = Image.open("img.png")
image = image.resize((380, 450))
original_image = image.resize((100, 100))
original_image = ImageTk.PhotoImage(original_image)
image = ImageTk.PhotoImage(image)

# Label(left_frame,  image=original_image).pack(fill='both',  padx=5,  pady=5)

# large_image = original_image.subsample(2,2)
# Label(right_frame,  image=image).pack(fill='both',  padx=5,  pady=5)
canvas = Canvas(right_frame, bg='grey', height=450)
canvas.pack(fill='both', expand=1, padx=5, pady=5)

canvas.bind("<Button-1>", get_x_and_y)
canvas.bind("<B1-Motion>", draw_smth)
canvas.bind('<Motion>', callback)

canvas.create_image(0, 0, image=image, anchor='nw')

tool_bar3 = Frame(right_frame, height=150, width=80, bg='lightgrey')
tool_bar3.pack(fill='both',padx=5,  pady=5)

# Button(tool_bar3, text='Select a Color',  command=change_color).grid(row=0,column=0, padx=5,  pady=5)
# Button( tool_bar3,text='delete line',command=delete_line).grid(row=0,column=1, padx=5,  pady=5)
# Spinbox(tool_bar3, from_=0, to=30, textvariable=width, wrap=True).grid(row=0,column=2, padx=5,  pady=5)

b=Button(tool_bar3, text='Select a Color', command=change_color)
b.pack(padx=5, pady=5)
Button(tool_bar3, text=' Delete Line   ', command=delete_line).pack(padx=5, pady=5)
Spinbox(tool_bar3, from_=0, to=30, textvariable=width, wrap=True).pack(padx=5, pady=5)

# ----------------------
tool_bar = Frame(left_frame, width=90, height=185, bg='lightgrey')
tool_bar.pack(side='left', fill='both', padx=5, pady=5, expand=True)

tool_bar2 = Frame(left_frame, width=90, height=185, bg='lightgrey')
tool_bar2.pack(side='right', fill='both', padx=5, pady=5, expand=True)


def clicked():
    '''if button is clicked, display message'''
    print("Clicked.")


# Example labels that serve as placeholders for other widgets
# Label(tool_bar,  text="Tools",  relief=RAISED).pack(anchor='n',  padx=5,  pady=3,  ipadx=10)
# Label(filter_bar,  text="Filters",  relief=RAISED).pack(anchor='n',  padx=5,  pady=3,  ipadx=10)

# For now, when the buttons are clicked, they only call the clicked() method. We will add functionality later.
# Create frames and labels in left_frame

Label(tool_bar, image=original_image).pack(fill='both', padx=5, pady=5)
Button(tool_bar, text="Rotate", command=clicked).pack(padx=5, pady=5)
Label(tool_bar, image=original_image).pack(fill='both', padx=5, pady=5)
Button(tool_bar, text="Scale", command=clicked).pack(padx=5, pady=5)
Label(tool_bar, image=original_image).pack(fill='both', padx=5, pady=5)
Button(tool_bar, text="Translate", command=clicked).pack(padx=5, pady=5)

Label(tool_bar2, image=original_image).pack(fill='both', padx=5, pady=5)
Button(tool_bar2, text="Wrap", command=clicked).pack(padx=5, pady=5)
Label(tool_bar2, image=original_image).pack(fill='both', padx=5, pady=5)
Button(tool_bar2, text="Skew", command=clicked).pack(padx=5, pady=5)
Label(tool_bar2, image=original_image).pack(fill='both', padx=5, pady=5)
Button(tool_bar2, text="Paint", command=clicked).pack(padx=5, pady=5)

root.mainloop()
