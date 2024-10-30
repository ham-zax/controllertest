"""Macro control panel component."""

import tkinter as tk
from tkinter import ttk
from src.utils.constants import BUTTON_NAMES

class MacroControls:
    def __init__(self, parent, macro_recorder):
        # Configure custom styles
        self.setup_styles()
        
        self.frame = ttk.LabelFrame(parent, text="Macro Controls", padding=10)
        self.frame.pack(fill="x", pady=5)
        self.macro_recorder = macro_recorder
        
        # Recording status indicator
        self.recording_status = tk.StringVar(value="Not Recording")
        self.status_label = ttk.Label(
            self.frame,
            textvariable=self.recording_status,
            style="Status.TLabel"
        )
        self.status_label.pack(fill="x", pady=(0, 10))
        
        self.setup_name_entry()
        self.setup_control_buttons()
        self.setup_management_controls()
        self.setup_button_assignment()
        self.setup_macro_list()

    def setup_styles(self):
        """Setup custom ttk styles."""
        style = ttk.Style()
        
        # Status label styles
        style.configure(
            "Status.TLabel",
            font=("Arial", 10, "bold"),
            padding=5,
            background="#f0f0f0",
            foreground="#666666"
        )
        
        # Button styles
        style.configure(
            "Record.TButton",
            padding=5,
            background="#ff4444"
        )
        
        style.configure(
            "Stop.TButton",
            padding=5,
            background="#666666"
        )
        
        style.configure(
            "Play.TButton",
            padding=5,
            background="#44ff44"
        )
        
        # Frame styles
        style.configure(
            "Controls.TFrame",
            padding=5,
            relief="solid"
        )

    def setup_name_entry(self):
        """Setup macro name entry field."""
        name_frame = ttk.Frame(self.frame, style="Controls.TFrame")
        name_frame.pack(fill="x", pady=5)
        
        name_label = ttk.Label(name_frame, text="Macro Name:")
        name_label.pack(side=tk.LEFT, padx=5)
        CreateToolTip(name_label, "Enter a unique name for your macro")
        
        self.macro_name = tk.StringVar()
        name_entry = ttk.Entry(
            name_frame,
            textvariable=self.macro_name,
            width=30
        )
        name_entry.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
        CreateToolTip(name_entry, "Enter a descriptive name for your macro")

    def setup_control_buttons(self):
        """Setup macro control buttons."""
        button_frame = ttk.Frame(self.frame, style="Controls.TFrame")
        button_frame.pack(fill="x", pady=5)
        
        record_btn = ttk.Button(
            button_frame,
            text="⏺ Start Recording",
            command=self.start_recording,
            style="Record.TButton"
        )
        record_btn.pack(side=tk.LEFT, padx=2, fill="x", expand=True)
        CreateToolTip(record_btn, "Start recording a new macro")
        
        stop_btn = ttk.Button(
            button_frame,
            text="⏹ Stop Recording",
            command=self.stop_recording,
            style="Stop.TButton"
        )
        stop_btn.pack(side=tk.LEFT, padx=2, fill="x", expand=True)
        CreateToolTip(stop_btn, "Stop recording the current macro")
        
        play_btn = ttk.Button(
            button_frame,
            text="▶ Play Macro",
            command=self.play_macro,
            style="Play.TButton"
        )
        play_btn.pack(side=tk.LEFT, padx=2, fill="x", expand=True)
        CreateToolTip(play_btn, "Play the selected macro")
        
        stop_play_btn = ttk.Button(
            button_frame,
            text="⏹ Stop Playback",
            command=self.stop_playback,
            style="Stop.TButton"
        )
        stop_play_btn.pack(side=tk.LEFT, padx=2, fill="x", expand=True)
        CreateToolTip(stop_play_btn, "Stop macro playback")

    def setup_management_controls(self):
        """Setup macro management controls."""
        management_frame = ttk.Frame(self.frame, style="Controls.TFrame")
        management_frame.pack(fill="x", pady=5)
        
        delete_btn = ttk.Button(
            management_frame,
            text="🗑 Delete Macro",
            command=self.delete_macro
        )
        delete_btn.pack(side=tk.LEFT, padx=2)
        CreateToolTip(delete_btn, "Delete the selected macro")
        
        ttk.Label(management_frame, text="Speed:").pack(side=tk.LEFT, padx=2)
        self.speed_var = tk.StringVar(value="1.0")
        speed_entry = ttk.Entry(
            management_frame,
            textvariable=self.speed_var,
            width=5
        )
        speed_entry.pack(side=tk.LEFT, padx=2)
        CreateToolTip(speed_entry, "Playback speed multiplier (1.0 = normal speed)")
        
        adjust_btn = ttk.Button(
            management_frame,
            text="⚡ Adjust Timing",
            command=self.adjust_timing
        )
        adjust_btn.pack(side=tk.LEFT, padx=2)
        CreateToolTip(adjust_btn, "Adjust the timing of the selected macro")

    def setup_button_assignment(self):
        """Setup button assignment controls."""
        assign_frame = ttk.Frame(self.frame, style="Controls.TFrame")
        assign_frame.pack(fill="x", pady=5)
        
        assign_label = ttk.Label(assign_frame, text="Assign to:")
        assign_label.pack(side=tk.LEFT, padx=2)
        CreateToolTip(assign_label, "Select a button to assign the macro to")
        
        # Create a mapping of friendly names to internal names
        self.friendly_to_internal = {BUTTON_NAMES[k]: k for k in ['BTN_TR', 'BTN_TL', 'BTN_NORTH', 'BTN_SOUTH', 'BTN_EAST', 'BTN_WEST']}
        friendly_names = list(self.friendly_to_internal.keys())
        
        self.button_var = tk.StringVar()
        button_combo = ttk.Combobox(
            assign_frame,
            textvariable=self.button_var,
            values=friendly_names,
            width=15
        )
        button_combo.pack(side=tk.LEFT, padx=2)
        CreateToolTip(button_combo, "Choose a controller button")
        
        assign_btn = ttk.Button(
            assign_frame,
            text="🎮 Assign",
            command=self.assign_macro
        )
        assign_btn.pack(side=tk.LEFT, padx=2)
        CreateToolTip(assign_btn, "Assign the macro to the selected button")

    def setup_macro_list(self):
        """Setup macro list display."""
        list_frame = ttk.LabelFrame(self.frame, text="Saved Macros", padding=5)
        list_frame.pack(fill="both", expand=True, pady=5)
        
        # Create a frame for the listbox and scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill="both", expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        
        # Configure listbox with custom colors and font
        self.macro_listbox = tk.Listbox(
            list_container,
            height=8,
            selectmode=tk.SINGLE,
            font=("Arial", 10),
            bg="#ffffff",
            fg="#333333",
            selectbackground="#0078d7",
            selectforeground="#ffffff",
            yscrollcommand=scrollbar.set
        )
        self.macro_listbox.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Configure scrollbar
        scrollbar.config(command=self.macro_listbox.yview)
        
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
            self.recording_status.set("🔴 Recording...")
            self.status_label.configure(foreground="#ff0000")

    def stop_recording(self):
        """Stop recording the current macro."""
        name = self.macro_name.get().strip()
        if name:
            self.macro_recorder.stop_recording(name)
            self.update_macro_list()
            self.recording_status.set("Not Recording")
            self.status_label.configure(foreground="#666666")

    def play_macro(self):
        """Play the selected macro."""
        selection = self.macro_listbox.curselection()
        if selection:
            name = self.macro_listbox.get(selection[0])
            self.macro_recorder.play_macro(name)
            self.recording_status.set("▶ Playing Macro...")
            self.status_label.configure(foreground="#00aa00")

    def stop_playback(self):
        """Stop macro playback."""
        self.macro_recorder.stop_playback()
        self.recording_status.set("Not Recording")
        self.status_label.configure(foreground="#666666")

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
        friendly_button = self.button_var.get()
        selection = self.macro_listbox.curselection()
        if friendly_button and selection:
            name = self.macro_listbox.get(selection[0])
            # Convert friendly name back to internal name
            internal_button = self.friendly_to_internal.get(friendly_button)
            if internal_button:
                self.macro_recorder.assign_macro(name, internal_button)

class CreateToolTip:
    """Create a tooltip for a given widget."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(
            self.tooltip,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            padding=2
        )
        label.pack()

    def leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def setup_macro_controls(parent, macro_recorder):
    """Create and return a new MacroControls instance."""
    return MacroControls(parent, macro_recorder)
