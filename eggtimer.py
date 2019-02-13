import time
import json
from tkinter import *
from colour import Color

# Font used application wide
g_font_name = "Verdana"
g_color_bg = '#cdcdcd'
g_color_alarm = '#ff0000'


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


class timer():
    """Handles states."""

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
                data = json.load(f)['seconds']
                if type(data) == int:
                    return data
                else:
                    return 240
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
        #print('running, seconds: ', self.get_time_in_secs())
        self.seconds = self.get_time_in_secs()
        self.set_seconds_to_file(self.seconds)

        self.create_or_set_state(state_run)

    def change_state_to_alarm(self):
        self.create_or_set_state(state_alarm)

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
            #print(f'{new_state} state exists')
        else:
            self.state = new_state(self)
            self.states[new_state] = self.state
            #print(f'{new_state} state doesnt exist')

    def get_time_from_secs(self, seconds):
        """Converts seconds to hours, minutes and seconds"""
        hrs = int(seconds / 3600)
        mins = int((seconds % 3600) / 60)
        secs = int(seconds % 60)
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
        self.timer = timer
        self.font_name = g_font_name
        self.columns = 5
        self.rows = 3
        self.row_height = 160
        self.init_elements()
        self.enable()

    def init_elements(self):

        # Container
        self.state_frame = Frame(self.timer.root, bg=g_color_bg)
        setup_grid(self.state_frame, self.columns, self.rows, self.row_height)
        self.state_frame.grid(sticky=NSEW)

        # State header
        self.header_text = StringVar()
        self.state_header = Label(
            self.state_frame, font=(self.font_name, 24), textvariable=self.header_text, bg=g_color_bg)
        self.state_header.grid(row=0, columnspan=self.columns)

    def disable(self):
        self.state_frame.grid_remove()

    def enable(self):
        if not self.state_frame.grid_info():
            self.state_frame.grid()


class state_set(timer_state):
    """State for setting the timer."""

    def init_elements(self):

        super().init_elements()

        self.header_text.set('Set time:')

        # Digit container
        digit_input_frame = Frame(self.state_frame, bg=g_color_bg)
        digit_input_frame.grid(row=1, columnspan=self.columns)
        setup_grid(digit_input_frame, 5, 4, 0)

        # Digit inputs
        time = self.timer.get_time_from_secs(self.timer.seconds)
        self.input_hrs = digit_input(digit_input_frame,
                                     time['hrs'], 'h', 1, max_value=99)
        self.input_mins = digit_input(
            digit_input_frame, time['mins'], 'min', 2)
        self.input_secs = digit_input(digit_input_frame, time['secs'], 's', 3)

        # Start button
        self.button_start = Button(self.state_frame, height=1,
                                   width=5, font=(self.font_name, 24), text='Start', command=self.start_timer)
        self.button_start.grid(
            row=2, columnspan=self.columns)

    def start_timer(self):
        self.timer.change_state_to_run()
        self.button_start.focus()


class state_run(timer_state):
    """State for setting the timer."""

    def __init__(self, root):
        self.time_left = 0
        self.time_var = StringVar()
        self.time_paused = 0  # When timer was paused
        super().__init__(root)

        self.timer.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def init_elements(self):

        super().init_elements()

        self.header_text.set('Time remaining:')

        # Time output
        time_output = Entry(self.state_frame, width=8,
                            font=(self.font_name, 44), justify=CENTER, textvariable=self.time_var)
        time_output['state'] = 'readonly'
        time_output.grid(row=1, columnspan=self.columns)

        # Buttons
        self.button_start = Button(self.state_frame, height=1,
                                   width=5, font=(self.font_name, 24), text='Start', command=self.start)
        self.button_start.grid(row=2, column=1)
        self.button_start.grid_remove()

        self.button_pause = Button(self.state_frame, height=1,
                                   width=5, font=(self.font_name, 24), text='Pause', command=self.pause)
        self.button_pause.grid(row=2, column=1)

        self.button_stop = Button(self.state_frame, height=1,
                                  width=5, font=(self.font_name, 24), text='Stop', command=self.stop)
        self.button_stop.grid(row=2, column=3)

    def enable(self):
        super().enable()
        self.time_left = self.timer.seconds
        self.update_time_var()
        self.start()

    def update_time_var(self):
        time_dict = self.timer.get_time_from_secs(self.time_left)

        # Add leading zero to single digits
        # for key, value in time_dict.items():
        #     if value < 10:
        #         time_dict[key] = '0' + str(value)

        hrs = time_dict['hrs']
        mins = time_dict['mins']
        secs = time_dict['secs']

        if not hrs and not mins:
            self.time_var.set(f"{secs}")
        elif not hrs:
            self.time_var.set(f"{mins}.{secs}")
        else:
            self.time_var.set(f"{hrs}.{mins}.{secs}")

    def start(self):
        self.is_running = True
        self.run()
        self.button_pause.grid()

    def pause(self):
        self.is_running = False
        self.button_pause.grid_remove()
        self.button_start.grid()
        self.time_paused = time.time()

    def stop(self):
        self.is_running = False
        self.timer.change_state_to_set()
        self.button_stop.focus()

    def run(self):

        if self.is_running:

            # Check if a second has passed since timer was paused so it can run again
            if self.time_paused + 1 >= time.time():
                # When the timer can start running again
                start_time = self.time_paused + 1 - time.time()
                self.timer.root.after(int(1000 * start_time), self.run)
                return
            else:
                self.time_paused = 0

            # Alarm if time's up
            if self.time_left <= 0:
                self.is_running = False
                self.alarm()

            # Update time field and rerun after a second
            self.update_time_var()
            self.timer.root.after(1000, self.run)
            self.time_left -= 1
            self.time_left = max(0, self.time_left)

    def alarm(self):
        self.timer.change_state_to_alarm()

    def on_closing(self):
        """Stop threaded timer on app close"""
        self.timer.root.destroy()


class state_alarm(timer_state):
    """State for setting the timer."""

    def __init__(self, root):

        self.color_scale = self.get_alarm_colors()
        super().__init__(root)
        self.timer.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def init_elements(self):

        super().init_elements()

        self.header_text.set('Time is up!')

        self.button_ok = Button(self.state_frame, height=1,
                                width=5, font=(self.font_name, 24), text='OK', command=self.shut_alarm)
        self.button_ok.grid(row=2, column=2)

    def enable(self):
        super().enable()
        self.color_change_direction = 1
        self.current_color_index = 0
        self.set_bg_color(g_color_bg)
        self.play_alarm()

    def get_alarm_colors(self):
        color1 = Color(g_color_bg)
        color2 = Color(g_color_alarm)
        return list(color1.range_to(color2, 30))

    def play_alarm(self):

        self.set_next_color()
        self.after_id = self.timer.root.after(30, self.play_alarm)

    def set_next_color(self):

        #print(self.current_color_index, len(self.color_scale))
        self.set_bg_color(self.color_scale[self.current_color_index])

        if self.color_change_direction > 0:
            if self.current_color_index < len(self.color_scale) - 1:
                self.current_color_index += 1
            else:
                self.color_change_direction = -1
                self.current_color_index -= 1
        else:
            if self.current_color_index > 0:
                self.current_color_index -= 1
            else:
                self.color_change_direction = 1
                self.current_color_index += 1

    def set_bg_color(self, color):

        self.state_frame.configure(background=color)
        self.state_header.configure(background=color)

    def shut_alarm(self):
        self.timer.root.after_cancel(self.after_id)
        self.timer.change_state_to_set()

    def on_closing(self):
        """Stop threaded timer on app close"""
        self.shut_alarm()
        self.timer.root.destroy()


class digit_input():

    def __init__(self, frame, value, text, column, max_value=59):

        global g_font_name
        self.font_name = g_font_name
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
        self.unit_text = Label(frame, text=text, font=(self.font_name, 12), bg=g_color_bg).grid(
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
