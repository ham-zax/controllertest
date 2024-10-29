"""Debug information panel component."""

import tkinter as tk
from tkinter import ttk

class DebugPanel:
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Debug Information", padding=10)
        self.frame.pack(fill="x", pady=5)
        
        self.debug_label = ttk.Label(
            self.frame,
            text="Raw Input Values:\nNo input received",
            font=('Arial', 10),
            justify=tk.LEFT
        )
        self.debug_label.pack(pady=5)
        
        self.debug_info = {}

    def update_info(self, event):
        """Update debug information display."""
        self.debug_info[event.code] = event.state
        debug_text = "Raw Input Values:\n"
        for code, value in self.debug_info.items():
            debug_text += f"{code}: {value}\n"
        self.debug_label.config(text=debug_text)

def setup_debug_info(parent):
    """Create and return a DebugPanel instance."""
    return DebugPanel(parent)
