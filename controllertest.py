"""Xbox controller input counter and visualizer using tkinter."""

import tkinter as tk
from datetime import datetime
from inputs import get_gamepad
from time import time
import threading


class ControllerCounter:
    """
    A class to track and display Xbox controller inputs with a GUI interface.
    
    Provides real-time input tracking, input history, and input counting features.
    """

    def __init__(self):
        """Initialize the controller counter and setup the GUI."""
        self.window = tk.Tk()
        self.window.title("Xbox Controller Input Counter")
        self.window.geometry("800x600")
        
        # Current input frame
        current_frame = tk.LabelFrame(
            self.window,
            text="Current Input Status",
            padx=10,
            pady=10
        )
        current_frame.pack(fill="x", padx=10, pady=5)
        
        self.current_input_label = tk.Label(
            current_frame,
            text="No input",
            font=('Arial', 12)
        )
        self.current_input_label.pack(pady=5)
        
        # Counter frame
        counter_frame = tk.LabelFrame(
            self.window,
            text="1-Second Counter",
            padx=10,
            pady=10
        )
        counter_frame.pack(fill="x", padx=10, pady=5)
        
        self.counter_label = tk.Label(
            counter_frame,
            text="Current count (1s): 0",
            font=('Arial', 12)
        )
        self.counter_label.pack(pady=5)
        
        self.last_count_label = tk.Label(
            counter_frame,
            text="Previous count: 0",
            font=('Arial', 12)
        )
        self.last_count_label.pack(pady=5)
        
        # Input history frame
        history_frame = tk.LabelFrame(
            self.window,
            text="Input History",
            padx=10,
            pady=10
        )
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create text widget for history
        self.history_text = tk.Text(history_frame, height=15, width=50)
        self.history_text.pack(fill="both", expand=True)
        
        # Scrollbar for history
        scrollbar = tk.Scrollbar(history_frame, command=self.history_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.config(yscrollcommand=scrollbar.set)
        
        # Initialize counters and timing
        self.press_count = 0
        self.last_reset = time()
        self.last_count = 0
        
        # Button mapping for clearer names
        self.button_names = {
            'BTN_NORTH': 'Y Button',
            'BTN_SOUTH': 'A Button',
            'BTN_EAST': 'B Button',
            'BTN_WEST': 'X Button',
            'BTN_TR': 'R1',
            'BTN_TL': 'L1',
            'ABS_RZ': 'R2',
            'ABS_Z': 'L2',
            'ABS_HAT0Y': {-1: 'D-Pad Up', 1: 'D-Pad Down'},
            'ABS_HAT0X': {-1: 'D-Pad Left', 1: 'D-Pad Right'}
        }
        
        # Button state tracking
        self.button_states = {}
        
        # Trigger thresholds
        self.trigger_threshold = 100  # Adjust based on controller
        
        # Flag for thread control
        self.running = True
        
        # Start controller input thread
        self.controller_thread = threading.Thread(target=self.read_controller)
        self.controller_thread.daemon = True
        self.controller_thread.start()

    def add_to_history(self, input_name, state, timestamp=None):
        """Add an input event to the history display."""
        if timestamp is None:
            timestamp = datetime.now()
        
        timestamp_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
        state_str = "pressed" if state else "released"
        history_entry = f"[{timestamp_str}] {input_name} {state_str}\n"
        
        # Add to text widget and auto-scroll
        self.history_text.insert(tk.END, history_entry)
        self.history_text.see(tk.END)

    def update_counter(self):
        """Update the input counter and handle one-second resets."""
        current_time = time()
        
        # If more than a second has passed
        if current_time - self.last_reset >= 1:
            # Store the last count before resetting
            self.last_count = self.press_count
            self.last_count_label.config(
                text=f"Previous count: {self.last_count}"
            )
            
            # Reset counter
            self.press_count = 0
            self.last_reset = current_time
        
        self.press_count += 1
        self.counter_label.config(
            text=f"Current count (1s): {self.press_count}"
        )

    def read_controller(self):
        """Read and process controller inputs in a separate thread."""
        while self.running:
            try:
                events = get_gamepad()
                for event in events:
                    current_time = datetime.now()
                    
                    # Handle regular buttons
                    if event.ev_type == 'Key':
                        if event.code in self.button_names:
                            button_name = self.button_names[event.code]
                            self.window.after(
                                0,
                                lambda b=button_name, s=event.state, t=current_time:
                                self.handle_input(b, bool(s), t)
                            )
                    
                    # Handle triggers (R2/L2)
                    elif event.ev_type == 'Absolute':
                        if event.code in ['ABS_RZ', 'ABS_Z']:
                            button_name = self.button_names[event.code]
                            is_pressed = event.state > self.trigger_threshold
                            
                            # Only register state change if crosses threshold
                            current_state = self.button_states.get(
                                button_name,
                                False
                            )
                            if current_state != is_pressed:
                                self.button_states[button_name] = is_pressed
                                self.window.after(
                                    0,
                                    lambda b=button_name, s=is_pressed,
                                    t=current_time: self.handle_input(b, s, t)
                                )
                        
                        # Handle D-pad
                        elif (event.code in self.button_names and
                              event.state in self.button_names[event.code]):
                            direction = self.button_names[event.code][event.state]
                            self.window.after(
                                0,
                                lambda d=direction, s=True, t=current_time:
                                self.handle_input(d, s, t)
                            )
                            
            except Exception as e:
                self.window.after(
                    0,
                    lambda: self.current_input_label.config(
                        text="Controller disconnected or error occurred"
                    )
                )

    def handle_input(self, input_name, is_pressed, timestamp):
        """Process and display a controller input event."""
        # Update current input display
        state_str = "pressed" if is_pressed else "released"
        self.current_input_label.config(
            text=f"Current Input: {input_name} ({state_str})"
        )
        
        # Add to history
        self.add_to_history(input_name, is_pressed, timestamp)
        
        # Update counter only on press
        if is_pressed:
            self.update_counter()

    def run(self):
        """Start the application main loop."""
        try:
            self.window.mainloop()
        finally:
            self.running = False


if __name__ == "__main__":
    counter = ControllerCounter()
    counter.run()
