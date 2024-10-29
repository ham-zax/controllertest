"""Xbox controller input counter and visualizer using tkinter."""

import tkinter as tk
from datetime import datetime
from inputs import get_gamepad
from time import time
import threading
import math


class ControllerCounter:
    """
    A class to track and display Xbox controller inputs with a GUI interface.
    
    Provides real-time input tracking, input history, and input counting features.
    Includes analog stick position tracking and debugging information.
    """

    def __init__(self):
        """Initialize the controller counter and setup the GUI."""
        self.window = tk.Tk()
        self.window.title("Xbox Controller Input Counter")
        self.window.geometry("1000x800")
        
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

        # Analog sticks frame
        analog_frame = tk.LabelFrame(
            self.window,
            text="Analog Sticks",
            padx=10,
            pady=10
        )
        analog_frame.pack(fill="x", padx=10, pady=5)

        # Left stick status
        self.left_stick_label = tk.Label(
            analog_frame,
            text="Left Stick: Center",
            font=('Arial', 12)
        )
        self.left_stick_label.pack(pady=5)

        # Right stick status
        self.right_stick_label = tk.Label(
            analog_frame,
            text="Right Stick: Center",
            font=('Arial', 12)
        )
        self.right_stick_label.pack(pady=5)

        # Debug info frame
        debug_frame = tk.LabelFrame(
            self.window,
            text="Debug Information",
            padx=10,
            pady=10
        )
        debug_frame.pack(fill="x", padx=10, pady=5)

        self.debug_label = tk.Label(
            debug_frame,
            text="Raw Input Values:\nNo input received",
            font=('Arial', 10),
            justify=tk.LEFT
        )
        self.debug_label.pack(pady=5)
        
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

        # Analog stick states
        self.analog_states = {
            'LEFT': {'X': 0, 'Y': 0},
            'RIGHT': {'X': 0, 'Y': 0}
        }
        
        # Analog stick mapping
        self.analog_mapping = {
            'ABS_X': ('LEFT', 'X'),
            'ABS_Y': ('LEFT', 'Y'),
            'ABS_RX': ('RIGHT', 'X'),
            'ABS_RY': ('RIGHT', 'Y')
        }

        # Analog stick thresholds and calibration
        self.analog_threshold = 3000  # Minimum movement to register
        self.analog_max = 32768  # Maximum analog value
        self.analog_deadzone = 0.1  # 10% deadzone
        
        # Button state tracking
        self.button_states = {}
        
        # Trigger thresholds
        self.trigger_threshold = 100  # Adjust based on controller
        
        # Debug information
        self.debug_info = {}
        
        # Flag for thread control
        self.running = True
        
        # Start controller input thread
        self.controller_thread = threading.Thread(target=self.read_controller)
        self.controller_thread.daemon = True
        self.controller_thread.start()

    def get_analog_direction(self, x, y):
        """Convert analog stick coordinates to direction and magnitude."""
        # Normalize values to -1 to 1 range
        x_norm = x / self.analog_max
        y_norm = -y / self.analog_max  # Invert Y axis to match standard coordinates

        # Calculate magnitude (distance from center)
        magnitude = math.sqrt(x_norm**2 + y_norm**2)
        
        # Apply deadzone
        if magnitude < self.analog_deadzone:
            return "Center", 0

        # Calculate angle in degrees
        angle = math.degrees(math.atan2(y_norm, x_norm))
        if angle < 0:
            angle += 360

        # Convert angle to cardinal direction
        directions = [
            "East", "Northeast", "North", "Northwest",
            "West", "Southwest", "South", "Southeast"
        ]
        index = int((angle + 22.5) / 45) % 8
        direction = directions[index]

        # Return direction and magnitude as percentage
        return direction, round(magnitude * 100)

    def update_analog_display(self, stick, x, y):
        """Update the display for analog stick position."""
        direction, magnitude = self.get_analog_direction(x, y)
        
        if stick == 'LEFT':
            self.left_stick_label.config(
                text=f"Left Stick: {direction} ({magnitude}%)"
            )
        else:
            self.right_stick_label.config(
                text=f"Right Stick: {direction} ({magnitude}%)"
            )

        # Log significant movements
        if magnitude > 0:
            self.add_to_history(
                f"{stick.title()} Stick",
                True,
                None,
                f"{direction} ({magnitude}%)"
            )

    def add_to_history(self, input_name, state, timestamp=None, extra_info=None):
        """Add an input event to the history display."""
        if timestamp is None:
            timestamp = datetime.now()
        
        timestamp_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
        if extra_info:
            history_entry = f"[{timestamp_str}] {input_name}: {extra_info}\n"
        else:
            state_str = "pressed" if state else "released"
            history_entry = f"[{timestamp_str}] {input_name} {state_str}\n"
        
        # Add to text widget and auto-scroll
        self.history_text.insert(tk.END, history_entry)
        self.history_text.see(tk.END)

    def update_debug_info(self, event):
        """Update debug information display."""
        self.debug_info[event.code] = event.state
        debug_text = "Raw Input Values:\n"
        for code, value in self.debug_info.items():
            debug_text += f"{code}: {value}\n"
        self.debug_label.config(text=debug_text)

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
                    
                    # Update debug information
                    self.window.after(
                        0,
                        lambda e=event: self.update_debug_info(e)
                    )
                    
                    # Handle regular buttons
                    if event.ev_type == 'Key':
                        if event.code in self.button_names:
                            button_name = self.button_names[event.code]
                            self.window.after(
                                0,
                                lambda b=button_name, s=event.state, t=current_time:
                                self.handle_input(b, bool(s), t)
                            )
                    
                    # Handle analog inputs
                    elif event.ev_type == 'Absolute':
                        if event.code in self.analog_mapping:
                            stick, axis = self.analog_mapping[event.code]
                            self.analog_states[stick][axis] = event.state
                            
                            # Update analog display
                            x = self.analog_states[stick]['X']
                            y = self.analog_states[stick]['Y']
                            if abs(x) > self.analog_threshold or abs(y) > self.analog_threshold:
                                self.window.after(
                                    0,
                                    lambda s=stick, x=x, y=y:
                                    self.update_analog_display(s, x, y)
                                )
                        
                        # Handle triggers (R2/L2)
                        elif event.code in ['ABS_RZ', 'ABS_Z']:
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
                        text=f"Controller error: {str(e)}"
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
