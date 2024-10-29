"""Input history panel component."""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

class HistoryPanel:
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Input History", padding=10)
        self.frame.pack(fill="both", expand=True, pady=5)
        
        self.history_text = tk.Text(self.frame, height=15, width=50)
        self.history_text.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(self.frame, command=self.history_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.config(yscrollcommand=scrollbar.set)

    def add_entry(self, input_name: str, state: bool, timestamp=None, extra_info=None):
        """Add an input event to the history display."""
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            timestamp_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
            if extra_info:
                history_entry = f"[{timestamp_str}] {input_name}: {extra_info}\n"
            else:
                state_str = "pressed" if state else "released"
                history_entry = f"[{timestamp_str}] {input_name} {state_str}\n"
            
            self.history_text.insert(tk.END, history_entry)
            self.history_text.see(tk.END)
        except Exception as e:
            print(f"Error adding to history: {e}")

def setup_history(parent):
    """Create and return a HistoryPanel instance."""
    return HistoryPanel(parent)
