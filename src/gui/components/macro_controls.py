"""Macro control panel component."""

import tkinter as tk
from tkinter import ttk

class MacroControls:
    def __init__(self, parent, macro_recorder):
        self.frame = ttk.LabelFrame(parent, text="Macro Controls", padding=10)
        self.frame.pack(fill="x", pady=5)
        self.macro_recorder = macro_recorder
        
        self.setup_name_entry()
        self.setup_control_buttons()
        self.setup_management_controls()
        self.setup_button_assignment()
        self.setup_macro_list()

    def setup_name_entry(self):
        """Setup macro name entry field."""
        name_frame = ttk.Frame(self.frame)
        name_frame.pack(fill="x", pady=5)
        
        ttk.Label(name_frame, text="Macro Name:").pack(side=tk.LEFT, padx=5)
        self.macro_name = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.macro_name).pack(side=tk.LEFT, fill="x", expand=True, padx=5)

    def setup_control_buttons(self):
        """Setup macro control buttons."""
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill="x", pady=5)
        
        ttk.Button(
            button_frame,
            text="Start Recording",
            command=self.start_recording
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="Stop Recording",
            command=self.stop_recording
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="Play Macro",
            command=self.play_macro
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="Stop Playback",
            command=self.stop_playback
        ).pack(side=tk.LEFT, padx=2)

    def setup_management_controls(self):
        """Setup macro management controls."""
        management_frame = ttk.Frame(self.frame)
        management_frame.pack(fill="x", pady=5)
        
        ttk.Button(
            management_frame,
            text="Delete Macro",
            command=self.delete_macro
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(management_frame, text="Speed:").pack(side=tk.LEFT, padx=2)
        self.speed_var = tk.StringVar(value="1.0")
        ttk.Entry(
            management_frame,
            textvariable=self.speed_var,
            width=5
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            management_frame,
            text="Adjust Timing",
            command=self.adjust_timing
        ).pack(side=tk.LEFT, padx=2)

    def setup_button_assignment(self):
        """Setup button assignment controls."""
        assign_frame = ttk.Frame(self.frame)
        assign_frame.pack(fill="x", pady=5)
        
        ttk.Label(assign_frame, text="Assign to:").pack(side=tk.LEFT, padx=2)
        self.button_var = tk.StringVar()
        button_combo = ttk.Combobox(
            assign_frame,
            textvariable=self.button_var,
            values=['BTN_TR', 'BTN_TL', 'BTN_NORTH', 'BTN_SOUTH', 'BTN_EAST', 'BTN_WEST']
        )
        button_combo.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            assign_frame,
            text="Assign",
            command=self.assign_macro
        ).pack(side=tk.LEFT, padx=2)

    def setup_macro_list(self):
        """Setup macro list display."""
        list_frame = ttk.Frame(self.frame)
        list_frame.pack(fill="x", pady=5)
        
        ttk.Label(list_frame, text="Saved Macros:").pack(anchor="w")
        
        self.macro_listbox = tk.Listbox(list_frame, height=5)
        self.macro_listbox.pack(fill="x", pady=5)
        self.update_macro_list()

    def update_macro_list(self):
        """Update the macro listbox with saved macros."""
        self.macro_listbox.delete(0, tk.END)
        for name in self.macro_recorder.saved_macros:
            self.macro_listbox.insert(tk.END, name)

    def start_recording(self):
        """Start recording a new macro."""
        name = self.macro_name.get().strip()
        if name:
            self.macro_recorder.recording = True
            self.macro_recorder.current_macro = []

    def stop_recording(self):
        """Stop recording the current macro."""
        name = self.macro_name.get().strip()
        if name:
            self.macro_recorder.stop_recording(name)
            self.update_macro_list()

    def play_macro(self):
        """Play the selected macro."""
        selection = self.macro_listbox.curselection()
        if selection:
            name = self.macro_listbox.get(selection[0])
            self.macro_recorder.play_macro(name)

    def stop_playback(self):
        """Stop macro playback."""
        self.macro_recorder.stop_playback()

    def delete_macro(self):
        """Delete the selected macro."""
        selection = self.macro_listbox.curselection()
        if selection:
            name = self.macro_listbox.get(selection[0])
            self.macro_recorder.delete_macro(name)
            self.update_macro_list()

    def adjust_timing(self):
        """Adjust timing of the selected macro."""
        try:
            speed = float(self.speed_var.get())
            selection = self.macro_listbox.curselection()
            if selection:
                name = self.macro_listbox.get(selection[0])
                self.macro_recorder.adjust_timing(name, speed)
        except ValueError:
            pass

    def assign_macro(self):
        """Assign macro to a button."""
        button = self.button_var.get()
        selection = self.macro_listbox.curselection()
        if button and selection:
            name = self.macro_listbox.get(selection[0])
            self.macro_recorder.assign_macro(name, button)

def setup_macro_controls(parent, macro_recorder):
    """Create and return a new MacroControls instance."""
    return MacroControls(parent, macro_recorder)
