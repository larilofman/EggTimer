import time
import json
from tkinter import *

# Font used application wide
G_FONT_NAME = "Verdana"

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

    setup_grid(root, 1, 1)

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

    # print(element.grid_size())


class timer():
    """Handles user input and states."""

    def __init__(self, root):
        self.seconds = self.get_seconds_from_file()
        self.state = None
        self.root = root
        self.states = {}
        self.change_state_to_set()

    def get_seconds_from_file(self):
        """Returns seconds from json or 240 on exception."""
        try:
            with open('time.json') as f:
                return json.load(f)['seconds']
        except:
            return 240

    def set_seconds_to_file(self, seconds):
        """Saves seconds to json file"""

        with open('time.json', 'w') as f:
            data = {'seconds': seconds}
            json.dump(data, f, indent=2)

    def change_state_to_set(self):
        self.create_or_set_state(state_set, 'set')

    def change_state_to_run(self):
        print('running, seconds: ', self.get_time_in_secs())
        self.set_seconds_to_file(self.get_time_in_secs())

        self.create_or_set_state(state_run, 'run')

    def create_or_set_state(self, new_state, state_name):

        if self.state:
            self.state.disable()

        if self.states.get(state_name):
            self.state = self.states.get(state_name)
            self.state.enable()
            print(f'{state_name} state exists')
        else:
            self.state = new_state(self)
            self.states[state_name] = self.state
            print(f'{state_name} state doesnt exist')

    def get_time_from_secs(self):

        hrs = int(self.seconds / 3600)
        mins = int((self.seconds % 3600) / 60)
        secs = int(self.seconds % 60)
        return {'hrs': hrs, 'mins': mins, 'secs': secs}

    def get_time_in_secs(self):
        hrs = int(self.state.input_hrs.get_value())
        mins = int(self.state.input_mins.get_value())
        secs = int(self.state.input_secs.get_value())
        total_seconds = hrs*3600 + mins*60 + secs
        return total_seconds


class timer_state():
    """Base class for all states"""

    def disable(self):
        self.state_frame.grid_remove()

    def enable(self):
        self.state_frame.grid()


class state_set(timer_state):
    """State for setting the timer."""

    def __init__(self, timer):
        global G_FONT_NAME
        self.timer = timer
        self.font_name = G_FONT_NAME
        self.columns = 5
        self.rows = 3
        self.init_elements()

    def init_elements(self):

        # Container elements
        self.state_frame = Frame(self.timer.root)
        setup_grid(self.state_frame, self.columns, self.rows)
        self.state_frame.grid(sticky=NSEW)
        digit_input_frame = Frame(self.state_frame)
        digit_input_frame.grid(row=1, columnspan=self.columns)
        setup_grid(digit_input_frame, 5, 4)

        # State header
        Label(self.state_frame, text="Set time",
              font=(self.font_name, 24)).grid(row=0, columnspan=self.columns, pady=(30, 0))

        # Digit inputs
        time = self.timer.get_time_from_secs()
        self.input_hrs = digit_input(digit_input_frame,
                                     time['hrs'], 'h', 1, max_value=99)
        self.input_mins = digit_input(
            digit_input_frame, time['mins'], 'min', 2)
        self.input_secs = digit_input(digit_input_frame, time['secs'], 's', 3)

        # Start button
        self.button_start = Button(self.state_frame, height=1,
                                   width=5, font=(self.font_name, 24), text='Start', command=self.run)
        self.button_start.grid(
            row=2, columnspan=self.columns, pady=(0, 30))

    def run(self):
        self.timer.change_state_to_run()
        self.button_start.focus()


class digit_input():

    def __init__(self, frame, value, text, column, max_value=59):

        global G_FONT_NAME
        self.font_name = G_FONT_NAME
        self.frame = frame
        self.max_value = max_value

        # Entry field
        self.vcmd = self.frame.register(self.validate_digits)
        self.value = StringVar(value=value)
        self.digit_field = Entry(self.frame, width=2, font=(
            self.font_name, 24), validate='all', validatecommand=(self.vcmd, '%P'), justify=CENTER, textvariable=self.value)
        self.digit_field.grid(row=1, column=column, padx=5)
        self.digit_field.bind("<Button-1>", self.on_click)
        self.digit_field.bind("<FocusOut>", self.on_focus_out)

        # Buttons
        self.button_plus = Button(frame, height=2, width=5,
                                  text="+", command=self.add)
        self.button_plus.grid(row=0, column=column, padx=5)

        self.button_minus = Button(frame, height=2, width=5,
                                   text="-", command=self.substract)
        self.button_minus.grid(row=2, column=column, padx=5)

        # Unit text
        self.unit_text = Label(frame, text=text, font=(self.font_name, 12)).grid(
            row=4, column=column)

    def get_value(self):
        if self.value.get():
            return int(self.value.get())
        else:  # Empty field
            return 0

    def on_click(self, event):
        """Set 0 value to empty"""
        if self.get_value() == 0:
            self.value.set('')

    def on_focus_out(self, event):
        """Sets empty value to zero and limits value to max"""
        if not self.get_value():
            self.value.set(0)
        elif int(self.get_value()) > self.max_value:
            self.value.set(self.max_value)

    def validate_digits(self, P):
        """Accepts value of two digits or empty"""
        if len(P) < 3 and str.isdigit(P) or P == "":
            return True
        else:
            return False

    def add(self):
        """Adds one to value or rotates over to 0 if over max"""
        self.digit_field.focus()

        new_value = self.get_value() + 1

        if new_value > self.max_value:
            new_value = 0

        self.value.set(new_value)

    def substract(self):
        """Removes one from value or rotates over to max if under 0"""
        self.digit_field.focus()

        new_value = self.get_value() - 1

        if new_value < 0:
            new_value = self.max_value

        self.value.set(new_value)


class state_run(timer_state):
    """State for setting the timer."""

    def __init__(self, timer):
        global G_FONT_NAME
        self.timer = timer
        self.font_name = G_FONT_NAME
        self.columns = 5
        self.rows = 3
        self.init_elements()

    def init_elements(self):

        # Container elements
        self.state_frame = Frame(self.timer.root)
        setup_grid(self.state_frame, self.columns, self.rows)
        self.state_frame.grid(sticky=NSEW)
        # digit_input_frame = Frame(self.state_frame)
        # digit_input_frame.grid(row=1, columnspan=self.columns)
        # setup_grid(digit_input_frame, 5, 4)

        # State header
        Label(self.state_frame, text="Time remaining:",
              font=(self.font_name, 24)).grid(row=0, columnspan=self.columns, pady=(30, 0))

        # Digit inputs
        # time = self.timer.get_time_from_secs()
        # self.input_hrs = digit_input(digit_input_frame,
        #                              time['hrs'], 'h', 1, max_value=99)
        # self.input_mins = digit_input(
        #     digit_input_frame, time['mins'], 'min', 2)
        # self.input_secs = digit_input(digit_input_frame, time['secs'], 's', 3)

        # Buttons
        self.button_stop = Button(self.state_frame, height=1,
                                  width=5, font=(self.font_name, 24), text='Stop', command=self.stop)
        self.button_stop.grid(
            row=2, columnspan=self.columns, pady=(0, 30))

    def stop(self):
        self.timer.change_state_to_set()
        self.button_stop.focus()


init_app()
