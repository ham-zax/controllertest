"""Counter display component."""

import tkinter as tk
from tkinter import ttk
import time

class Counter:
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="1-Second Counter", padding=10)
        self.frame.pack(fill="x", pady=5)
        
        self.counter_label = ttk.Label(
            self.frame,
            text="Current count (1s): 0",
            font=('Arial', 12)
        )
        self.counter_label.pack(pady=5)
        
        self.last_count_label = ttk.Label(
            self.frame,
            text="Previous count: 0",
            font=('Arial', 12)
        )
        self.last_count_label.pack(pady=5)
        
        self.press_count = 0
        self.last_reset = time.time()
        self.last_count = 0

    def update(self):
        """Update the press counter."""
        current_time = time.time()
        if current_time - self.last_reset >= 1.0:
            self.last_count = self.press_count
            self.last_count_label.config(text=f"Previous count: {self.last_count}")
            self.press_count = 1
            self.last_reset = current_time
        else:
            self.press_count += 1
        
        self.counter_label.config(text=f"Current count (1s): {self.press_count}")

def setup_counter(parent):
    """Create and return a Counter instance."""
    return Counter(parent)
