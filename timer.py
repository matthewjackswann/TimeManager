import tkinter as tk
from tkinter import ttk
import time
from datetime import datetime
import os
import csv
import sys
from notify import notification

# TIMER_LENGTH = 60 * 30 # in seconds
TIMER_LENGTH = 10 # in seconds how long you have before still working check
TIMEOUT_LENGTH = 5 # in seconds how long you have to click continue working before stopping
DATA_LOCATION = "./data"

assert TIMEOUT_LENGTH < TIMER_LENGTH

def load_timers(listbox):
    for f in os.listdir(DATA_LOCATION):
        if (os.path.isfile(f"{DATA_LOCATION}/{f}")) and f.endswith(".csv"):
            listbox.insert(tk.END, f[:-4])

def time_to_datetime(sec):
    return datetime.fromtimestamp(sec).strftime("%B %d, %I:%M:%S")

def sec_to_hms(sec):
    h = sec // (60 * 60)
    m = (sec // 60) % 60
    s = sec % 60
    return h, m, s

def alive_check():
    popup = tk.Toplevel()
    popup.title("Alive Check")

    notification('Time manager', message='Alive Check', app_name='Time Manager')
    os.system('play -nq -t alsa synth 1 sine 440') # play sound

    def dead_callback():
        stop_timer()
        root.after_cancel(dead_timeout)
        popup.destroy()

    def alive_callback():
        root.after_cancel(dead_timeout)
        popup.destroy()

    dead_timeout = root.after(TIMEOUT_LENGTH * 1000, dead_callback)

    alive = tk.Button(popup, text="I'm still here", command=alive_callback)
    dead = tk.Button(popup, text="I've Stopped Working", command=dead_callback)

    alive.pack()
    dead.pack()


def clock_tick():
    global start_time, timer_running, next_stop_time, timer_display, time_spent, total_time # i know this is bad
    if timer_running:
        curr_time = int(time.time())
        time_passed = curr_time - start_time # in seconds
        if curr_time > next_stop_time:
            alive_check()
            next_stop_time += TIMER_LENGTH
        h, m, s = sec_to_hms(time_passed)
        timer_display.set(f'{h:02}:{m:02}:{s:02}')
        h, m, s = sec_to_hms(time_passed + total_time)
        time_spent.set(f'Total time spent: {h:02}:{m:02}:{s:02}')
        root.after(1000, clock_tick)

def timer_button_callback():
    global timer_running, current_timer
    if current_timer == -1:
        return
    if timer_running: # stop timer
        stop_timer()
    else: # start timer
        start_timer()

def start_timer():
    global timer_running, start_time, next_stop_time, button_text # i know this is bad
    timer_running = True
    button_text.set("Stop Work")
    start_time = int(time.time())
    next_stop_time = start_time + TIMER_LENGTH
    clock_tick()

def stop_timer():
    global timer_running, button_text, start_time, current_timer, timers # i know this is bad
    button_text.set("Start Work")
    timer_running = False
    end_time = int(time.time())
    date = time_to_datetime(start_time)
    h, m, s = sec_to_hms(end_time - start_time)
    with open(f"{DATA_LOCATION}/{timers.get(current_timer)}.csv", "a") as file:
        file.write(f'{date},{h},{m},{s}\n')

def timer_changed(event):
    global current_timer, timer_label, total_time # i know this is bad
    selection = event.widget.curselection()
    if selection:
        if timer_running: # undo, can't change while timer is running
            event.widget.selection_clear(0, tk.END)
            event.widget.select_set(current_timer)
        else:
            current_timer = event.widget.curselection()[0]
            t = event.widget.get(current_timer)
            timer_label.set(t)
            total_time = 0
            with open(f"{DATA_LOCATION}/{t}.csv", "r") as file:
                for line in file:
                    if line.strip() == "":
                        continue
                    _, _, h, m, s = line.split(",")
                    total_time += (60 * 60 * int(h)) + (60 * int(m)) + int(s)
            timer_display.set("00:00:00")
            h, m, s = sec_to_hms(total_time)
            time_spent.set(f'Total time spent: {h:02}:{m:02}:{s:02}')

root = tk.Tk()
root.title("Time manager")
# Theme taken from https://github.com/rdbende/Azure-ttk-theme
root.tk.call("source", "azure.tcl")
root.tk.call("set_theme", "dark")

big_frame = ttk.Frame(root)
big_frame.pack(fill="both", expand=True)

timer_box = tk.Label(big_frame)
timer_display = tk.StringVar(big_frame, '00:00:00')
timer_box['textvariable'] = timer_display

timer_label_e = tk.Label(big_frame)
timer_label = tk.StringVar(big_frame)
timer_label_e['textvariable'] = timer_label

time_spent_e = tk.Label(big_frame)
time_spent = tk.StringVar(big_frame, "Total time spent: 00:00:00")
time_spent_e['textvariable'] = time_spent

timer_running = False
start_time = 0
next_stop_time = 1
total_time = 0

button = ttk.Button(big_frame, command=timer_button_callback)
button_text = tk.StringVar(big_frame, "Start Work")
button['textvariable'] = button_text

current_timer = -1

timers = tk.Listbox(big_frame)
timers.bind('<<ListboxSelect>>', timer_changed)

load_timers(timers)

time_spent_e.pack()
timer_label_e.pack()
timer_box.pack()
button.pack()
timers.pack()
root.mainloop()
