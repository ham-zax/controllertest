"""Input history panel component."""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

class HistoryPanel:
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Input History", padding=10)
        self.frame.pack(fill="both", expand=True, pady=5)
        
        # Create a frame to contain the Text widget and scrollbar
        self.text_frame = ttk.Frame(self.frame)
        self.text_frame.pack(fill="both", expand=True)
        self.text_frame.grid_propagate(False)  # Prevent frame from resizing
        
        # Configure grid weights
        self.text_frame.grid_columnconfigure(0, weight=1)
        self.text_frame.grid_rowconfigure(0, weight=1)
        
        self.history_text = tk.Text(self.text_frame, height=15, width=50, wrap=tk.WORD)
        self.history_text.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(self.text_frame, command=self.history_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.history_text.config(yscrollcommand=scrollbar.set)

    def add_entry(self, input_name: str, state: bool, timestamp=None, extra_info=None):
        """Add an input event to the history display."""
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            timestamp_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
            
            # Handle analog stick inputs
            if input_name in ["LEFT", "RIGHT"]:
                if isinstance(extra_info, tuple) and len(extra_info) == 2:
                    direction, magnitude = extra_info
                    history_entry = f"[{timestamp_str}] {input_name} Stick: {direction} ({magnitude}%)\n"
                else:
                    history_entry = f"[{timestamp_str}] {input_name} Stick moved\n"
            else:
                # Handle button inputs
                state_str = "pressed" if state else "released"
                history_entry = f"[{timestamp_str}] {input_name} {state_str}\n"
            
            self.history_text.insert(tk.END, history_entry)
            self.history_text.see(tk.END)
            
            # Limit history to last 1000 lines to prevent excessive memory usage
            line_count = int(self.history_text.index('end-1c').split('.')[0])
            if line_count > 1000:
                self.history_text.delete("1.0", "2.0")
                
        except Exception as e:
            print(f"Error adding to history: {e}")

def setup_history(parent):
    """Create and return a HistoryPanel instance."""
    return HistoryPanel(parent)
