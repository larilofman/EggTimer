# EggTimer
Timer application made with Python

Timer:
- keeps user defined time saved in a settings file
- time is handled as seconds

Timer has four states: set, run, paused, alarm

Set state:
- set digit for hours, minutes and seconds with either keyboard input or clicking an adjust button
- start button

Run state:
- big output box showing time remaining, updated every second
- stop button which changes state to set
- pause button which changes state to paused

Paused state:
- big output box showing time remaining, paused
- start button

Alarm state:
- big output box showing informative text
- screen flashing with red color
- plays an alarm sound
- big ok button