import time
import json
from tkinter import *

# Font used application wide
G_FONT_NAME = "Verdana"


def init_app():
    """Sets up application window and starts loop."""

    root = Tk()
    root.geometry("480x480")
    root.resizable(False, False)

    setup_grid(root, 1, 1, 0)

    root.title('EggTimer')
    root.call('wm', 'iconphoto', root._w, PhotoImage(file='icon.png'))
    maintimer = timer(root)
    root.mainloop()


def setup_grid(element, columns, rows, row_height):
    """Create a grid of the size columns*rows on element."""

    for c in range(0, columns):
        element.columnconfigure(c, weight=1)

    for r in range(0, rows):
        element.rowconfigure(r, weight=1, minsize=row_height)

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
        self.create_or_set_state(state_set)

    def change_state_to_run(self):
        print('running, seconds: ', self.get_time_in_secs())
        self.set_seconds_to_file(self.get_time_in_secs())

        self.create_or_set_state(state_run)

    def create_or_set_state(self, new_state):
        """Sets state to a new one

        Disables old state.
        Finds new state from dictionary or creates and adds it.
        Key: class
        Value: instance
        """

        if self.state:
            self.state.disable()

        if self.states.get(new_state):
            self.state = self.states.get(new_state)
            self.state.enable()
            print(f'{new_state} state exists')
        else:
            self.state = new_state(self)
            self.states[new_state] = self.state
            print(f'{new_state} state doesnt exist')

    def get_time_from_secs(self):
        """Converts seconds to hours, minutes and seconds"""
        hrs = int(self.seconds / 3600)
        mins = int((self.seconds % 3600) / 60)
        secs = int(self.seconds % 60)
        return {'hrs': hrs, 'mins': mins, 'secs': secs}

    def get_time_in_secs(self):
        """Converts hours, minutes and seconds to seconds"""
        hrs = int(self.state.input_hrs.get_value())
        mins = int(self.state.input_mins.get_value())
        secs = int(self.state.input_secs.get_value())
        total_seconds = hrs*3600 + mins*60 + secs
        return total_seconds


class timer_state():
    """Base class for all states"""

    def __init__(self, timer):
        global G_FONT_NAME
        self.timer = timer
        self.font_name = G_FONT_NAME
        self.columns = 5
        self.rows = 3
        self.row_height = 160
        self.init_elements()

    def init_elements(self):

        # Container
        self.state_frame = Frame(self.timer.root)
        setup_grid(self.state_frame, self.columns, self.rows, self.row_height)
        self.state_frame.grid(sticky=NSEW)

        # State header
        Label(self.state_frame, text="Set time",
              font=(self.font_name, 24)).grid(row=0, columnspan=self.columns)

    def disable(self):
        self.state_frame.grid_remove()

    def enable(self):
        self.state_frame.grid()


class state_set(timer_state):
    """State for setting the timer."""

    def init_elements(self):

        super().init_elements()

        # Digit container
        digit_input_frame = Frame(self.state_frame)
        digit_input_frame.grid(row=1, columnspan=self.columns)
        setup_grid(digit_input_frame, 5, 4, 0)

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
            row=2, columnspan=self.columns)

    def run(self):
        self.timer.change_state_to_run()
        self.button_start.focus()


class state_run(timer_state):
    """State for setting the timer."""

    def init_elements(self):

        super().init_elements()

        # Buttons
        self.button_stop = Button(self.state_frame, height=1,
                                  width=5, font=(self.font_name, 24), text='Stop', command=self.stop)
        self.button_stop.grid(
            row=2, columnspan=self.columns)

    def stop(self):
        self.timer.change_state_to_set()
        self.button_stop.focus()


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


init_app()
