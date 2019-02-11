import time
import json
from tkinter import *

# Font used application wide
font_name = "Verdana"

# Timer:
# - keeps user defined time saved in a settings file
# - time is handled as seconds

# Timer has four states: set, run, paused, alarm

# Set state:
# - input box for hours, minutes and seconds
# - start button

# Run state:
# - big output box showing time remaining, updated every second
# - stop button which changes state to set
# - pause button which changes state to paused

# Paused state:
# - big output box showing time remaining, paused
# - start button

# Alarm state:
# - big output box showing informative text
# - screen flashing with red color
# - plays an alarm sound
# - big ok button


def init_app():
    """Sets up application window and starts loop."""

    root = Tk()
    root.geometry("480x480")
    root.resizable(False, False)

    setup_grid(root, 5, 3)

    root.title('EggTimer')
    root.call('wm', 'iconphoto', root._w, PhotoImage(file='icon.png'))
    maintimer = timer(root)
    root.mainloop()


def setup_grid(element, columns, rows):
    """Create a grid of the size columns*rows on element."""

    for c in range(0, columns):
        element.columnconfigure(c, weight=1)

    for r in range(0, rows):
        element.rowconfigure(r, weight=1)

    print(element.grid_size())


class timer():
    """Handles user input and states."""

    def __init__(self, root):
        self.seconds = self.get_seconds_from_file()
        self.state = None
        self.root = root
        self.change_state_to_set()

    def get_seconds_from_file(self):
        """Returns seconds from json or 240 on exception."""
        try:
            with open('time.json') as f:
                return json.load(f)['seconds']
        except:
            return 240

    def change_state_to_set(self):
        self.state = state_set(self)

    def get_root_width(self):
        """Returns amount of columns on the root object"""
        return self.root.grid_size()[0]


class state_set():
    """State for setting the timer."""

    def __init__(self, timer):
        global font_name
        self.timer = timer
        print(timer.seconds)
        self.font_name = font_name
        self.init_elements()

    def init_elements(self):

        Label(self.timer.root, text="Set time",
              font=(self.font_name, 24)).grid(row=0, columnspan=self.timer.get_root_width(), pady=(30, 0))

        element_frame = Frame(self.timer.root)
        element_frame.grid(row=1, columnspan=self.timer.get_root_width())
        setup_grid(element_frame, 5, 4)

        hours = self.add_digit_input(element_frame, 'h', 1)
        minutes = self.add_digit_input(element_frame, 'min', 2)
        seconds = self.add_digit_input(element_frame, 's', 3)

        button_run = Button(self.timer.root, height=1,
                            width=5, font=(self.font_name, 24), text='Start')
        button_run.grid(
            row=2, columnspan=self.timer.get_root_width(), pady=(0, 30))

    def digit_callback(self, P):
        if len(P) < 3 and str.isdigit(P) or P == "":
            return True
        else:
            return False

    def add_digit_input(self, frame, text, object_index):

        vcmd = (frame.register(self.digit_callback))

        digit_field = Entry(frame, width=2, font=(
            self.font_name, 24), validate='all', validatecommand=(vcmd, '%P'), justify=CENTER)
        digit_field.grid(row=1, column=object_index, padx=5)

        button_plus = Button(frame, height=2, width=5, text="+")
        button_plus.grid(row=0, column=object_index, padx=5)

        button_minus = Button(frame, height=2, width=5, text="-")
        button_minus.grid(row=2, column=object_index, padx=5)

        Label(frame, text=text, font=(self.font_name, 12)).grid(
            row=4, column=object_index)


init_app()
