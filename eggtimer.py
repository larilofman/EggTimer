import time
import json
from tkinter import *

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
    """
    Sets up application window and starts loop.
    """

    root = Tk()
    root.geometry("480x480")
    root.resizable(False, False)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.title('EggTimer')
    root.call('wm', 'iconphoto', root._w, PhotoImage(file='icon.png'))
    maintimer = timer(root)
    root.mainloop()


class timer():
    """
    Handles user input and states.
    """

    def __init__(self, root):
        self.time = self.get_time_from_file()
        self.state = None
        self.root = root
        self.change_state_to_set()

    def get_time_from_file(self):
        """
        Returns time from time.json or returns 240 on exception.
        """
        try:
            with open('time.json') as f:
                return json.load(f)['time']
        except:
            return 240

    def change_state_to_set(self):
        self.state = state_set(self)


class state_set():
    """
    State for setting the timer.
    """

    def __init__(self, timer):
        self.timer = timer
        print(timer.time)
        self.init_elements()

    def init_elements(self):

        element_frame = Frame(self.timer.root, bg="brown", padx=120, pady=80,
                              width=480, height=480)
        Label(element_frame, text="Set time",
              font=('Verdana', 24)).grid(row=0, column=1)
        Frame(element_frame, height=100).grid(row=1, column=1)
        hours = self.add_digit_input(element_frame, 0)
        minutes = self.add_digit_input(element_frame, 1)
        seconds = self.add_digit_input(element_frame, 2)

        element_frame.grid(ipady=60)

    def add_digit_input(self, frame, object_index):

        button_plus = Button(frame, height=2, width=5, text="+")
        button_plus.grid(row=2, column=object_index, padx=5)

        digit_field = Entry(frame, width=7)
        digit_field.grid(row=3, column=object_index, padx=5)

        button_minus = Button(frame, height=2, width=5, text="-")
        button_minus.grid(row=4, column=object_index, padx=5)


init_app()
