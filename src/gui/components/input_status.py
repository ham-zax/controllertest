"""Input status display component."""

import tkinter as tk
from tkinter import ttk
import time

class InputStatus:
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Current Input Status", padding=10)
        self.frame.pack(fill="x", pady=5)
        
        self.input_label = ttk.Label(self.frame, text="No input", font=('Arial', 12))
        self.input_label.pack(pady=5)
        
        self.timer_label = ttk.Label(self.frame, text="Time: 0s", font=('Arial', 12))
        self.timer_label.pack(pady=5)
        
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        """Update the timer display."""
        elapsed = int(time.time() - self.start_time)
        self.timer_label.config(text=f"Time: {elapsed}s")
        self.frame.after(1000, self.update_timer)

    def update_input(self, input_name, is_pressed):
        """Update the current input display."""
        self.input_label.config(
            text=f"Current Input: {input_name} {'pressed' if is_pressed else 'released'}"
        )

def setup_input_status(parent):
    """Create and return an InputStatus instance."""
    return InputStatus(parent)
