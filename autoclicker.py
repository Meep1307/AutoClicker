import tkinter as tk
from tkinter import ttk
import threading
import time
from pynput.mouse import Button, Controller as MouseController
from pynput import keyboard

class AutoClicker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AutoClicker")
        self.geometry("300x170") # Increased height for hotkey label
        self.resizable(False, False)

        self.clicking = False
        self.click_thread = None
        self.mouse = MouseController()

        self.create_widgets()
        self.start_hotkey_listener()

    def create_widgets(self):
        self.status_label = ttk.Label(self, text="Status: Stopped")
        self.status_label.pack(pady=10)

        self.interval_label = ttk.Label(self, text="Click Interval (seconds):")
        self.interval_label.pack()

        self.interval_entry = ttk.Entry(self, width=10)
        self.interval_entry.insert(0, "0.01")
        self.interval_entry.pack()

        self.start_stop_button = ttk.Button(self, text="Start", command=self.toggle_clicking)
        self.start_stop_button.pack(pady=10)

        self.hotkey_label = ttk.Label(self, text="Hotkey: <ctrl>+<alt>+a to toggle")
        self.hotkey_label.pack()

    def toggle_clicking(self):
        # This function can be called from a different thread, so we need to be careful
        # when updating the GUI. We can use `self.after` to schedule the GUI update
        # on the main thread.
        if not self.clicking:
            self.after(0, self.start_clicking)
        else:
            self.after(0, self.stop_clicking)

    def start_clicking(self):
        try:
            interval = float(self.interval_entry.get())
            if interval <= 0:
                self.status_label.config(text="Status: Invalid interval")
                return
        except ValueError:
            self.status_label.config(text="Status: Invalid interval")
            return

        self.clicking = True
        self.status_label.config(text="Status: Running")
        self.start_stop_button.config(text="Stop")
        self.click_thread = threading.Thread(target=self.click_worker, args=(interval,))
        self.click_thread.daemon = True
        self.click_thread.start()

    def stop_clicking(self):
        self.clicking = False
        if self.click_thread:
            # No need to join, daemon thread will exit when main thread exits
            pass
        self.status_label.config(text="Status: Stopped")
        self.start_stop_button.config(text="Start")

    def click_worker(self, interval):
        while self.clicking:
            self.mouse.click(Button.left, 1)
            time.sleep(interval)

    def start_hotkey_listener(self):
        def on_activate():
            self.toggle_clicking()

        def for_canonical(f):
            return lambda k: f(l.canonical(k))

        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse('<ctrl>+<alt>+a'),
            on_activate)

        l = keyboard.Listener(
                on_press=for_canonical(hotkey.press),
                on_release=for_canonical(hotkey.release))
        l.daemon = True
        l.start()


if __name__ == "__main__":
    try:
        import pynput
    except ImportError:
        print("The 'pynput' library is not installed.")
        print("Please install it by running: pip install pynput")
    else:
        app = AutoClicker()
        app.mainloop()
