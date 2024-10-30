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
        
        # Define tags for different types of entries
        self.history_text.tag_configure("macro_event", foreground="blue")
        self.history_text.tag_configure("macro_input", foreground="green")
        
        scrollbar = ttk.Scrollbar(self.text_frame, command=self.history_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.history_text.config(yscrollcommand=scrollbar.set)

    def add_entry(self, input_name: str, state: bool, timestamp=None, extra_info=None, entry_type="normal"):
        """
        Add an input event to the history display.
        entry_type can be: "normal", "macro_playback", "macro_event"
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            timestamp_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
            
            # Handle analog stick inputs
            if input_name in ["LEFT", "RIGHT"]:
                if isinstance(extra_info, tuple) and len(extra_info) == 2:
                    direction, magnitude = extra_info
                    # Simplify direction names
                    direction_map = {
                        "North": "↓",
                        "South": "↑",
                        "East": "→",
                        "West": "←",
                        "Northeast": "↘",
                        "Northwest": "↙",
                        "Southeast": "↗",
                        "Southwest": "↖",
                        "up": "↑",
                        "down": "↓",
                        "left": "←",
                        "right": "→",
                        # Add analog stick specific mappings
                        "Up": "↑",
                        "Down": "↓",
                        "Left": "←",
                        "Right": "→",
                        "UpLeft": "↖",
                        "UpRight": "↗",
                        "DownLeft": "↙",
                        "DownRight": "↘"
                    }
                    simple_direction = direction_map.get(direction, direction)
                    history_entry = f"[{timestamp_str}] {input_name} Stick: {simple_direction} ({magnitude}%)\n"
                else:
                    history_entry = f"[{timestamp_str}] {input_name} Stick moved\n"
            else:
                # Handle button inputs
                state_str = "pressed" if state else "released"
                history_entry = f"[{timestamp_str}] {input_name} {state_str}\n"
            
            # Insert with appropriate tag based on entry type
            if entry_type == "macro_playback":
                self.history_text.insert(tk.END, history_entry, "macro_input")
            elif entry_type == "macro_event":
                self.history_text.insert(tk.END, history_entry, "macro_event")
            else:
                self.history_text.insert(tk.END, history_entry)
                
            self.history_text.see(tk.END)
            
            # Limit history to last 1000 lines to prevent excessive memory usage
            line_count = int(self.history_text.index('end-1c').split('.')[0])
            if line_count > 1000:
                self.history_text.delete("1.0", "2.0")
                
        except Exception as e:
            print(f"Error adding to history: {e}")

    def add_macro_event(self, event_type: str, details: str = None):
        """Add a macro-related event to the history."""
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
        
        event_messages = {
            "playback_start": "=== Macro Playback Started ===",
            "playback_end": "=== Macro Playback Completed ===",
            "record_start": "=== Macro Recording Started ===",
            "record_end": "=== Macro Recording Completed ===",
            "macro_error": "=== Macro Error ===",
            "macro_assign": "=== Macro Assignment ===",
            "macro_delete": "=== Macro Deleted ===",
            "macro_timing": "=== Macro Timing Adjusted ==="
        }
        
        message = event_messages.get(event_type, "=== Macro Event ===")
        history_entry = f"[{timestamp_str}] {message}\n"
        if details:
            history_entry += f"    {details}\n"
        self.history_text.insert(tk.END, history_entry, "macro_event")
        self.history_text.see(tk.END)

def setup_history(parent):
    """Create and return a HistoryPanel instance."""
    return HistoryPanel(parent)
