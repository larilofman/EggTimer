import time
import json
from tkinter import *
from colour import Color
import winsound

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

    main_timer = timer(root)

    add_menu(root, main_timer)

    root.mainloop()


def add_menu(root, timer):
    menu = Menu(root)
    root.config(menu=menu)

    mode_menu = Menu(menu, tearoff=0)
    menu.add_cascade(label="Timer mode", menu=mode_menu)
    mode_menu.add_command(label="Egg", command=empty_func)
    mode_menu.add_command(label="Pomodoro", command=empty_func)
    # mode_menu.add_separator()
    # mode_menu.add_command(label="Exit", command=empty_func)

    settings_menu = Menu(menu, tearoff=0)
    menu.add_cascade(label="Display mode", menu=settings_menu)
    settings_menu.add_radiobutton(
        label="h:m:s", variable=timer.display_mode, value=0, command=timer.toggle_display_mode)
    settings_menu.add_radiobutton(
        label="hh:mm:ss", variable=timer.display_mode, value=1, command=timer.toggle_display_mode)


def empty_func():
    pass


def setup_grid(element, columns, rows, row_height):
    """Create a grid of the size columns*rows on element."""

    for c in range(0, columns):
        element.columnconfigure(c, weight=1)

    for r in range(0, rows):
        element.rowconfigure(r, weight=1, minsize=row_height)


def play_audio():
    winsound.PlaySound('Radio-Interruption-SoundBible.com-1434341263.wav',
                       winsound.SND_LOOP + winsound.SND_ASYNC)


def stop_audio():
    winsound.PlaySound(None, winsound.SND_PURGE)


class timer():
    """Handles states."""

    def __init__(self, root):
        self.seconds = self.get_seconds_from_file()
        self.state = None
        self.root = root
        self.states = {}
        self.change_state_to_set()
        # Boolean for output having leading zeros
        self.display_mode = IntVar(value=self.load_setting('display_mode'))

    def get_seconds_from_file(self):
        """Returns seconds from json or 240 on exception."""
        try:
            with open('settings.json') as f:
                data = json.load(f)['seconds']
                if type(data) == int:
                    return data
                else:
                    return 240
        except:
            return 240

    # def set_seconds_to_file(self, seconds):
    #     """Saves seconds to json file"""

    #     with open('settings.json', 'w') as f:
    #         data = {'seconds': seconds}
    #         json.dump(data, f, indent=2)

    def change_state_to_set(self):
        self.create_or_set_state(state_set)

    def change_state_to_run(self):
        """Save time as seconds and change state to run"""
        self.seconds = self.get_time_in_secs()

        if self.seconds > 0:
            self.save_settings({'seconds': self.seconds})
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
        else:
            self.state = new_state(self)
            self.states[new_state] = self.state

    def get_time_from_secs(self, seconds):
        """Converts seconds to hours, minutes and seconds

        Also limits time to 99h 59min 59s
        """

        if seconds > 359999:
            seconds = 359999

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

    def toggle_display_mode(self):
        self.save_settings({'display_mode': self.display_mode.get()})

    def save_settings(self, json_entry):

        with open('settings.json') as f:
            data = json.load(f)

        with open('settings.json', 'w') as f:
            data.update(json_entry)
            json.dump(data, f, indent=2)

    def load_setting(self, json_key):
        with open('settings.json') as f:
            data = json.load(f)
            return data[json_key]


class timer_state():
    """Base class for all states"""

    def __init__(self, timer):
        self.timer = timer
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
            self.state_frame, font=(g_font_name, 24), textvariable=self.header_text, bg=g_color_bg)
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
        self.input_hrs = digit_input(
            digit_input_frame, time['hrs'], 'h', 1, self.check_if_can_start, max_value=99)
        self.input_mins = digit_input(
            digit_input_frame, time['mins'], 'min', 2, self.check_if_can_start)
        self.input_secs = digit_input(
            digit_input_frame, time['secs'], 's', 3, self.check_if_can_start)

        # Start button
        self.button_start = Button(self.state_frame, height=1,
                                   width=5, font=(g_font_name, 24), text='Start', command=self.start_timer)
        self.button_start.grid(
            row=2, columnspan=self.columns)

    def start_timer(self):

        for digit in (self.input_hrs, self.input_mins, self.input_secs):
            digit.clamp_value()

        self.timer.change_state_to_run()
        self.button_start.focus()

    def check_if_can_start(self, *kwargs):

        # Enable start button if there is a time set
        for digit in (self.input_hrs, self.input_mins, self.input_secs):
            if digit.get_value() > 0:
                self.button_start.config(state="normal")
                return

        self.button_start.config(state="disabled")


class state_run(timer_state):
    """State for setting the timer."""

    def __init__(self, root):
        self.time_left = 0
        self.time_var = StringVar()
        self.time_started = 0  # When was timer started
        self.time_paused = 0  # When was timer paused
        self.time_paused_total = 0  # How long has timer been paused for
        super().__init__(root)

    def init_elements(self):

        super().init_elements()

        self.header_text.set('Time remaining:')

        # Time output
        time_output = Entry(self.state_frame, width=8,
                            font=(g_font_name, 44), justify=CENTER, textvariable=self.time_var)
        time_output['state'] = 'readonly'
        time_output.grid(row=1, columnspan=self.columns, pady=(0, 24))

        # Buttons
        self.button_start = Button(self.state_frame, height=1, width=5, font=(
            g_font_name, 24), text='Start', command=self.start)
        self.button_start.grid(row=2, column=1)
        self.button_start.grid_remove()  # Hide start button at start

        self.button_pause = Button(self.state_frame, height=1,
                                   width=5, font=(g_font_name, 24), text='Pause', command=self.pause)
        self.button_pause.grid(row=2, column=1)

        self.button_stop = Button(self.state_frame, height=1,
                                  width=5, font=(g_font_name, 24), text='Stop', command=self.stop)
        self.button_stop.grid(row=2, column=3)

    def enable(self):
        super().enable()
        self.time_started = time.time()
        self.time_paused = 0
        self.time_paused_total = 0
        self.start()

    def update_time_var(self):

        time_dict = self.timer.get_time_from_secs(self.time_left)

        # Add leading zero to single digits
        if self.timer.display_mode.get():
            time_dict = self.get_time_with_zeros(time_dict)

        hrs = time_dict['hrs']
        mins = time_dict['mins']
        secs = time_dict['secs']

        if not hrs and not mins:
            self.time_var.set(f"{secs}")
        elif not hrs:
            self.time_var.set(f"{mins}:{secs}")
        else:
            self.time_var.set(f"{hrs}:{mins}:{secs}")

    def get_time_with_zeros(self, time):
        for key, value in time.items():
            if value < 10:
                time[key] = '0' + str(value)
        return time

    def start(self):
        """Starts the timer

        Also toggles the visible button and calculates total time spent paused
        """
        self.is_running = True
        self.button_start.grid_remove()
        self.button_pause.grid()

        if self.time_paused:
            self.time_paused_total += time.time() - self.time_paused

        self.run()

    def pause(self):
        """Pauses the timer and toggles visible button"""
        self.is_running = False
        self.button_pause.grid_remove()
        self.button_start.grid()
        self.time_paused = time.time()

    def stop(self):
        """Stops the timer and changes state to set"""
        self.is_running = False
        self.timer.change_state_to_set()
        self.button_stop.focus()

    def run(self):
        """Runs the timer

        Updates output field and calculates time remaining on every iteration.
        """
        if self.is_running:

            # Add timer duration and total time it's been paused to starting time and reduce current time
            self.time_left = self.time_started + self.timer.seconds + \
                self.time_paused_total - time.time()

            if self.time_left < 0:
                self.time_left = 0

            # Alarm if time's up
            if self.time_left <= 0:
                self.is_running = False
                self.alarm()

            # Update time field and rerun after a while
            self.update_time_var()
            self.timer.root.after(100, self.run)

    def alarm(self):
        self.timer.change_state_to_alarm()


class state_alarm(timer_state):
    """State for setting the timer."""

    def __init__(self, root):

        self.color_scale = self.get_alarm_colors()
        super().__init__(root)

    def init_elements(self):

        super().init_elements()

        self.header_text.set('Time is up!')

        self.button_ok = Button(self.state_frame, height=1,
                                width=5, font=(g_font_name, 24), text='OK', command=self.shut_alarm)
        self.button_ok.grid(row=2, column=2)

    def enable(self):
        super().enable()
        self.color_change_direction = 1
        self.current_color_index = 0
        self.set_bg_color(g_color_bg)
        self.change_color()
        self.start_alarm_sound()

    def get_alarm_colors(self):
        """Returns a list of color gradient"""
        color1 = Color(g_color_bg)
        color2 = Color(g_color_alarm)
        return list(color1.range_to(color2, 30))

    def change_color(self):
        """Flashes app background and plays a sound"""
        self.set_next_color()
        self.after_id = self.timer.root.after(30, self.change_color)

    def start_alarm_sound(self):
        play_audio()

    def set_next_color(self):

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
        stop_audio()


class digit_input():

    def __init__(self, frame, value, text, column, checker_func, max_value=59):

        self.frame = frame
        self.max_value = max_value

        # Entry field
        self.vcmd = self.frame.register(self.validate_digits)
        self.value = StringVar(value=value)
        self.value.trace_add('write', checker_func)
        self.digit_field = Entry(self.frame, width=2, font=(
            g_font_name, 24), validate='all', validatecommand=(self.vcmd, '%P'), justify=CENTER, textvariable=self.value)
        self.digit_field.grid(row=1, column=column, padx=5)
        self.digit_field.bind("<Button-1>", self.on_click)
        self.digit_field.bind("<FocusOut>", self.on_focus_out)

        # Buttons
        self.button_plus = Button(frame, height=1, width=3, font=(
            g_font_name, 14), text="+", command=self.add)
        self.button_plus.grid(row=0, column=column, padx=5)

        self.button_minus = Button(frame, height=1, width=3, font=(
            g_font_name, 14), text="-", command=self.substract)
        self.button_minus.grid(row=2, column=column, padx=5)

        # Unit text
        self.unit_text = Label(frame, text=text, font=(g_font_name, 12), bg=g_color_bg).grid(
            row=4, column=column)

    def get_value(self):
        return int(self.value.get()) if self.value.get() else 0

    def on_click(self, event):
        """Set 0 value to empty"""
        if self.get_value() == 0:
            self.value.set('')

    def on_focus_out(self, event):
        if self.value.get() == '00':
            self.value.set(0)
        self.clamp_value()

    def clamp_value(self):
        """Limits value between 0 and max"""
        if self.value.get():
            if int(self.value.get()) > self.max_value:
                self.value.set(self.max_value)
        else:
            self.value.set(0)

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
