"""Xbox controller input counter, macro recorder, and signal modifier."""

import json
import logging
import os
import sys
import threading
import time
import math
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from inputs import get_gamepad

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import inputs
        import vgamepad
        return True
    except ImportError as e:
        print(f"\nMissing dependency: {e}")
        print("Please install required packages using: pip install -r requirements.txt")
        return False

class MacroRecorder:
    """Records and plays back controller input sequences."""
    
    def __init__(self):
        self.recording = False
        self.current_macro = []
        self.saved_macros = {}
        self.macro_assignments = {}  # Maps buttons to macro names
        self.playback_active = False
        self.gamepad = vgamepad.VX360Gamepad()
        self.load_macros()
        self.loop_macro = False
        
        # Create default stick south + X macro
        self.create_stick_x_macro()

    def create_stick_x_macro(self):
        """Create a macro that pushes left stick south 100%, waits 0.1s, presses X, then releases both."""
        macro = [
            # Push left stick south 100%
            {'type': 'Absolute', 'code': 'ABS_Y', 'state': 32767, 'delay': 0},
            # Wait 0.1s
            {'type': 'Absolute', 'code': 'ABS_Y', 'state': 32767, 'delay': 0.1},
            # Press X
            {'type': 'Key', 'code': 'BTN_WEST', 'state': 1, 'delay': 0.1},
            # Release X and stick
            {'type': 'Key', 'code': 'BTN_WEST', 'state': 0, 'delay': 0.15},
            {'type': 'Absolute', 'code': 'ABS_Y', 'state': 0, 'delay': 0.15}
        ]
        self.saved_macros['stick_south_x'] = macro
        self.macro_assignments['BTN_TR'] = 'stick_south_x'  # Assign to R1 by default
        self.save_macros()

    def delete_macro(self, name):
        """Delete a macro and its assignments."""
        if name in self.saved_macros:
            del self.saved_macros[name]
            # Remove any assignments to this macro
            self.macro_assignments = {k: v for k, v in self.macro_assignments.items() if v != name}
            self.save_macros()
            return f"Deleted macro '{name}'"
        return f"Macro '{name}' not found"

    def adjust_timing(self, name, speed_factor):
        """Adjust the timing of a macro by a speed factor."""
        if name in self.saved_macros:
            macro = self.saved_macros[name]
            for event in macro:
                event['delay'] *= speed_factor
            self.save_macros()
            return f"Adjusted timing for macro '{name}'"
        return f"Macro '{name}' not found"

    def assign_macro(self, macro_name, button_code):
        """Assign a macro to a specific button."""
        if macro_name in self.saved_macros:
            self.macro_assignments[button_code] = macro_name
            self.save_macros()
            return f"Assigned macro '{macro_name}' to button {button_code}"
        return f"Macro '{macro_name}' not found"

    def save_macros(self):
        """Save macros and assignments to file."""
        try:
            data = {
                'macros': self.saved_macros,
                'assignments': self.macro_assignments
            }
            with open('macros.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving macros: {e}")

    def load_macros(self):
        """Load macros and assignments from file."""
        try:
            with open('macros.json', 'r') as f:
                data = json.load(f)
                self.saved_macros = data.get('macros', {})
                self.macro_assignments = data.get('assignments', {})
        except FileNotFoundError:
            self.saved_macros = {}
            self.macro_assignments = {}
        except Exception as e:
            print(f"Error loading macros: {e}")
            self.saved_macros = {}
            self.macro_assignments = {}

    def record_event(self, ev_type, code, state, timestamp):
        """Record a controller event."""
        if self.recording:
            delay = 0
            if self.current_macro:
                delay = timestamp - self.current_macro[-1]['timestamp']
            self.current_macro.append({
                'type': ev_type,
                'code': code,
                'state': state,
                'delay': delay,
                'timestamp': timestamp
            })

    def stop_recording(self, name=None):
        """Stop recording and optionally save the macro."""
        if not self.recording:
            return "Not currently recording"
        
        self.recording = False
        if not name or not self.current_macro:
            self.current_macro = []
            return "Recording cancelled"
        
        # Process the recorded events
        processed_macro = []
        for event in self.current_macro:
            processed_macro.append({
                'type': event['type'],
                'code': event['code'],
                'state': event['state'],
                'delay': event['delay']
            })
        
        self.saved_macros[name] = processed_macro
        self.save_macros()
        self.current_macro = []
        return f"Saved macro as '{name}'"

    def _playback_thread(self, events):
        """Thread function for macro playback."""
        while self.playback_active:
            for event in events:
                if not self.playback_active:
                    break
                
                time.sleep(event['delay'])
                
                if event['type'] == 'Key':
                    if event['state']:
                        self.gamepad.press_button(button=getattr(vgamepad.XUSB_BUTTON, event['code']))
                    else:
                        self.gamepad.release_button(button=getattr(vgamepad.XUSB_BUTTON, event['code']))
                elif event['type'] == 'Absolute':
                    if event['code'] == 'ABS_X':
                        self.gamepad.left_joystick_float(x_value_float=event['state'] / 32767.0, y_value_float=0.0)
                    elif event['code'] == 'ABS_Y':
                        self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=event['state'] / 32767.0)
                
                self.gamepad.update()
            
            if not self.loop_macro:
                self.playback_active = False

    def play_macro(self, name, loop=False):
        """Play back a recorded macro."""
        if name not in self.saved_macros:
            return f"Macro '{name}' not found"
        
        self.playback_active = True
        self.loop_macro = loop
        events = self.saved_macros[name]
        
        # Create a thread for playback
        thread = threading.Thread(target=self._playback_thread, args=(events,))
        thread.start()
        return f"Playing macro '{name}' {'(looping)' if loop else ''}"

    def stop_playback(self):
        """Stop macro playback."""
        self.playback_active = False
        self.loop_macro = False
        return "Stopped macro playback"

class ControllerCounter:
    def __init__(self):
        """Initialize the controller counter and setup the GUI."""
        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger('ControllerCounter')
        
        # Initialize variables
        self.running = True
        self.analog_max = 32767
        self.analog_threshold = 3000
        self.analog_deadzone = 0.1
        self.trigger_threshold = 100
        
        # Initialize button mappings
        self.button_names = {
            'BTN_NORTH': 'Y',
            'BTN_SOUTH': 'A',
            'BTN_EAST': 'B',
            'BTN_WEST': 'X',
            'BTN_TL': 'LB',
            'BTN_TR': 'RB',
            'BTN_SELECT': 'Back',
            'BTN_START': 'Start',
            'BTN_MODE': 'Guide',
            'BTN_THUMBL': 'LS',
            'BTN_THUMBR': 'RS',
            'ABS_Z': 'LT',
            'ABS_RZ': 'RT',
            'ABS_HAT0X': {-1: 'DPad Left', 1: 'DPad Right'},
            'ABS_HAT0Y': {-1: 'DPad Up', 1: 'DPad Down'}
        }
        
        self.analog_mapping = {
            'ABS_X': ('LEFT', 'X'),
            'ABS_Y': ('LEFT', 'Y'),
            'ABS_RX': ('RIGHT', 'X'),
            'ABS_RY': ('RIGHT', 'Y')
        }
        
        self.analog_states = {
            'LEFT': {'X': 0, 'Y': 0},
            'RIGHT': {'X': 0, 'Y': 0}
        }
        
        # Initialize macro recorder
        self.macro_recorder = MacroRecorder()

        self.window = tk.Tk()
        self.window.title("Xbox Controller Input Counter & Macro Recorder")
        self.window.geometry("1200x800")

        # Create main columns
        left_column = ttk.Frame(self.window)
        left_column.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        middle_column = ttk.Frame(self.window)
        middle_column.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        right_column = ttk.Frame(self.window)
        right_column.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        # Left Column - Input Status and Counter
        self.setup_input_status(left_column)
        self.setup_counter(left_column)
        
        # Middle Column - Analog Sticks and Debug
        self.setup_analog_display(middle_column)
        self.setup_debug_info(middle_column)
        
        # Right Column - Macro Controls and History
        self.setup_macro_controls(right_column)
        self.setup_history(right_column)

        # Initialize other variables
        self.press_count = 0
        self.last_reset = time.time()
        self.last_count = 0
        self.r1_pressed = False
        self.button_states = {}
        self.debug_info = {}

        # Start controller thread
        self.controller_thread = threading.Thread(target=self.read_controller)
        self.controller_thread.daemon = True
        self.controller_thread.start()

        # Set up window close handler
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_logging(self):
        """Setup logging configuration."""
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/controller_counter.log'),
                logging.StreamHandler()
            ]
        )

    def setup_input_status(self, parent):
        """Setup input status frame."""
        status_frame = ttk.LabelFrame(parent, text="Current Input Status", padding=10)
        status_frame.pack(fill="x", pady=5)
        
        self.current_input_label = ttk.Label(status_frame, text="No input", font=('Arial', 12))
        self.current_input_label.pack(pady=5)
        
        self.timer_label = ttk.Label(status_frame, text="Time: 0s", font=('Arial', 12))
        self.timer_label.pack(pady=5)
        
        self.start_time = time.time()
        self.update_timer()

    def setup_counter(self, parent):
        """Setup counter frame."""
        counter_frame = ttk.LabelFrame(parent, text="1-Second Counter", padding=10)
        counter_frame.pack(fill="x", pady=5)
        
        self.counter_label = ttk.Label(
            counter_frame,
            text="Current count (1s): 0",
            font=('Arial', 12)
        )
        self.counter_label.pack(pady=5)
        
        self.last_count_label = ttk.Label(
            counter_frame,
            text="Previous count: 0",
            font=('Arial', 12)
        )
        self.last_count_label.pack(pady=5)

    def setup_analog_display(self, parent):
        """Setup analog sticks frame."""
        analog_frame = ttk.LabelFrame(parent, text="Analog Sticks", padding=10)
        analog_frame.pack(fill="x", pady=5)
        
        self.left_stick_label = ttk.Label(
            analog_frame,
            text="Left Stick: Center",
            font=('Arial', 12)
        )
        self.left_stick_label.pack(pady=5)
        
        self.right_stick_label = ttk.Label(
            analog_frame,
            text="Right Stick: Center",
            font=('Arial', 12)
        )
        self.right_stick_label.pack(pady=5)

    def setup_debug_info(self, parent):
        """Setup debug information frame."""
        debug_frame = ttk.LabelFrame(parent, text="Debug Information", padding=10)
        debug_frame.pack(fill="x", pady=5)
        
        self.debug_label = ttk.Label(
            debug_frame,
            text="Raw Input Values:\nNo input received",
            font=('Arial', 10),
            justify=tk.LEFT
        )
        self.debug_label.pack(pady=5)

    def setup_macro_controls(self, parent):
        """Setup macro controls frame."""
        macro_frame = ttk.LabelFrame(parent, text="Macro Controls", padding=10)
        macro_frame.pack(fill="x", pady=5)

        # Macro name entry
        name_frame = ttk.Frame(macro_frame)
        name_frame.pack(fill="x", pady=5)
        
        ttk.Label(name_frame, text="Macro Name:").pack(side=tk.LEFT, padx=5)
        self.macro_name = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.macro_name).pack(side=tk.LEFT, fill="x", expand=True, padx=5)

        # Control buttons
        button_frame = ttk.Frame(macro_frame)
        button_frame.pack(fill="x", pady=5)
        
        ttk.Button(
            button_frame,
            text="Start Recording",
            command=self.start_macro_recording
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="Stop Recording",
            command=self.stop_macro_recording
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="Play Macro",
            command=self.play_selected_macro
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="Stop Playback",
            command=self.stop_macro_playback
        ).pack(side=tk.LEFT, padx=2)

        # Macro management
        management_frame = ttk.Frame(macro_frame)
        management_frame.pack(fill="x", pady=5)
        
        ttk.Button(
            management_frame,
            text="Delete Macro",
            command=self.delete_selected_macro
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
            command=self.adjust_macro_timing
        ).pack(side=tk.LEFT, padx=2)

        # Button assignment
        assign_frame = ttk.Frame(macro_frame)
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
            command=self.assign_macro_to_button
        ).pack(side=tk.LEFT, padx=2)

        # Macro list
        list_frame = ttk.Frame(macro_frame)
        list_frame.pack(fill="x", pady=5)
        
        ttk.Label(list_frame, text="Saved Macros:").pack(anchor="w")
        
        self.macro_listbox = tk.Listbox(list_frame, height=5)
        self.macro_listbox.pack(fill="x", pady=5)
        self.update_macro_list()

    def setup_history(self, parent):
        """Setup input history frame."""
        history_frame = ttk.LabelFrame(parent, text="Input History", padding=10)
        history_frame.pack(fill="both", expand=True, pady=5)
        
        self.history_text = tk.Text(history_frame, height=15, width=50)
        self.history_text.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(history_frame, command=self.history_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.config(yscrollcommand=scrollbar.set)

    def update_timer(self):
        """Update the timer display."""
        elapsed = int(time.time() - self.start_time)
        self.timer_label.config(text=f"Time: {elapsed}s")
        self.window.after(1000, self.update_timer)

    def update_counter(self):
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

    def update_macro_list(self):
        """Update the macro listbox with saved macros."""
        self.macro_listbox.delete(0, tk.END)
        for name in self.macro_recorder.saved_macros:
            self.macro_listbox.insert(tk.END, name)

    def start_macro_recording(self):
        """Start recording a new macro."""
        name = self.macro_name.get().strip()
        if not name:
            self.add_to_history("Macro Recording", False, None, "Please enter a macro name")
            return
        
        self.macro_recorder.recording = True
        self.macro_recorder.current_macro = []
        self.add_to_history("Macro Recording", True, None, f"Started recording macro: {name}")

    def stop_macro_recording(self):
        """Stop recording the current macro."""
        name = self.macro_name.get().strip()
        if not name:
            self.add_to_history("Macro Recording", False, None, "Please enter a macro name")
            return
        
        result = self.macro_recorder.stop_recording(name)
        self.add_to_history("Macro Recording", True, None, result)
        self.update_macro_list()

    def play_selected_macro(self):
        """Play the selected macro."""
        selection = self.macro_listbox.curselection()
        if selection:
            name = self.macro_listbox.get(selection[0])
            result = self.macro_recorder.play_macro(name)
            self.add_to_history("Macro Playback", True, None, result)
        else:
            self.add_to_history("Macro Playback", False, None, "No macro selected")

    def stop_macro_playback(self):
        """Stop macro playback."""
        result = self.macro_recorder.stop_playback()
        self.add_to_history("Macro Playback", False, None, result)

    def delete_selected_macro(self):
        """Delete the selected macro."""
        selection = self.macro_listbox.curselection()
        if selection:
            name = self.macro_listbox.get(selection[0])
            result = self.macro_recorder.delete_macro(name)
            self.add_to_history("Macro Manager", True, None, result)
            self.update_macro_list()

    def adjust_macro_timing(self):
        """Adjust the timing of the selected macro."""
        selection = self.macro_listbox.curselection()
        if not selection:
            self.add_to_history("Macro Manager", False, None, "No macro selected")
            return
            
        try:
            speed = float(self.speed_var.get())
            if speed <= 0:
                raise ValueError("Speed must be positive")
                
            name = self.macro_listbox.get(selection[0])
            result = self.macro_recorder.adjust_timing(name, speed)
            self.add_to_history("Macro Manager", True, None, result)
            
        except ValueError as e:
            self.add_to_history("Macro Manager", False, None, f"Invalid speed value: {e}")

    def assign_macro_to_button(self):
        """Assign the selected macro to a button."""
        selection = self.macro_listbox.curselection()
        button = self.button_var.get()
        
        if not selection:
            self.add_to_history("Macro Manager", False, None, "No macro selected")
            return
            
        if not button:
            self.add_to_history("Macro Manager", False, None, "No button selected")
            return
            
        name = self.macro_listbox.get(selection[0])
        result = self.macro_recorder.assign_macro(name, button)
        self.add_to_history("Macro Manager", True, None, result)

    def get_analog_direction(self, x: int, y: int) -> tuple[str, float]:
        """Convert analog stick coordinates to direction and magnitude."""
        try:
            x_norm = x / self.analog_max
            y_norm = -y / self.analog_max

            magnitude = math.sqrt(x_norm**2 + y_norm**2)
            
            if magnitude < self.analog_deadzone:
                return "Center", 0

            angle = math.degrees(math.atan2(y_norm, x_norm))
            if angle < 0:
                angle += 360

            directions = [
                "East", "Northeast", "North", "Northwest",
                "West", "Southwest", "South", "Southeast"
            ]
            index = int((angle + 22.5) / 45) % 8
            direction = directions[index]

            return direction, round(magnitude * 100)
        except Exception as e:
            self.logger.error(f"Error in get_analog_direction: {e}")
            return "Error", 0

    def update_analog_display(self, stick: str, x: int, y: int) -> None:
        """Update the display for analog stick position."""
        try:
            direction, magnitude = self.get_analog_direction(x, y)
            
            if stick == 'LEFT':
                self.left_stick_label.config(
                    text=f"Left Stick: {direction} ({magnitude}%)"
                )
            else:
                self.right_stick_label.config(
                    text=f"Right Stick: {direction} ({magnitude}%)"
                )

            if magnitude > 0:
                self.add_to_history(
                    f"{stick.title()} Stick",
                    True,
                    None,
                    f"{direction} ({magnitude}%)"
                )
        except Exception as e:
            self.logger.error(f"Error updating analog display: {e}")

    def add_to_history(self, input_name: str, state: bool, timestamp=None, extra_info=None) -> None:
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
            self.logger.error(f"Error adding to history: {e}")

    def update_debug_info(self, event) -> None:
        """Update debug information display with raw input values."""
        try:
            self.debug_info[event.code] = event.state
            debug_text = "Raw Input Values:\n"
            for code, value in self.debug_info.items():
                debug_text += f"{code}: {value}\n"
            self.debug_label.config(text=debug_text)
        except Exception as e:
            self.logger.error(f"Error updating debug info: {e}")

    def handle_input(self, input_name: str, is_pressed: bool, timestamp: datetime, event=None) -> None:
        """Process and display a controller input event."""
        try:
            if not isinstance(input_name, str):
                raise ValueError(f"Invalid input_name type: {type(input_name)}")
            if not isinstance(is_pressed, bool):
                raise ValueError(f"Invalid is_pressed type: {type(is_pressed)}")
            
            input_name = str(input_name)[:50]
            
            self.current_input_label.config(
                text=f"Current Input: {input_name} {'pressed' if is_pressed else 'released'}"
            )
            
            self.add_to_history(input_name, is_pressed, timestamp)
            
            # Update counter on press
            if is_pressed:
                self.update_counter()
            
            # Record event if macro recording is active
            if event and self.macro_recorder.recording:
                self.macro_recorder.record_event(
                    event.ev_type,
                    event.code,
                    event.state,
                    time.time()
                )
                
        except Exception as e:
            self.logger.error(f"Error handling input: {e}")

    def read_controller(self) -> None:
        """Read and process controller inputs in a separate thread."""
        reconnect_delay = 1
        max_reconnect_delay = 30
        
        while self.running:
            try:
                events = get_gamepad()
                reconnect_delay = 1
                
                for event in events:
                    if not self.running:
                        break
                        
                    current_time = datetime.now()
                    
                    self.window.after(
                        0,
                        lambda e=event: self.update_debug_info(e)
                    )
                    
                    if event.ev_type == 'Key':
                        if event.code in self.button_names:
                            button_name = self.button_names[event.code]
                            self.window.after(
                                0,
                                lambda b=button_name, s=event.state, t=current_time, e=event:
                                self.handle_input(b, bool(s), t, e)
                            )
                    
                    elif event.ev_type == 'Absolute':
                        if event.code in self.analog_mapping:
                            stick, axis = self.analog_mapping[event.code]
                            self.analog_states[stick][axis] = event.state
                            
                            x = self.analog_states[stick]['X']
                            y = self.analog_states[stick]['Y']
                            if abs(x) > self.analog_threshold or abs(y) > self.analog_threshold:
                                self.window.after(
                                    0,
                                    lambda s=stick, x=x, y=y:
                                    self.update_analog_display(s, x, y)
                                )
                        
                        elif event.code in ['ABS_RZ', 'ABS_Z']:
                            button_name = self.button_names[event.code]
                            is_pressed = event.state > self.trigger_threshold
                            
                            current_state = self.button_states.get(button_name, False)
                            if current_state != is_pressed:
                                self.button_states[button_name] = is_pressed
                                self.window.after(
                                    0,
                                    lambda b=button_name, s=is_pressed, t=current_time, e=event:
                                    self.handle_input(b, s, t, e)
                                )
                        
                        elif event.code in self.button_names and event.state in self.button_names[event.code]:
                            direction = self.button_names[event.code][event.state]
                            self.window.after(
                                0,
                                lambda d=direction, s=True, t=current_time, e=event:
                                self.handle_input(d, s, t, e)
                            )
                            
            except Exception as e:
                if self.running:
                    self.logger.error(f"Controller error: {e}")
                    self.window.after(
                        0,
                        lambda: self.current_input_label.config(
                            text=f"Controller disconnected. Attempting to reconnect..."
                        )
                    )
                    time.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)

    def run(self) -> None:
        """Start the application main loop."""
        try:
            self.window.mainloop()
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
        finally:
            self.running = False

    def on_closing(self) -> None:
        """Handle application shutdown gracefully."""
        try:
            self.logger.info("Application shutting down...")
            self.running = False
            
            if self.controller_thread.is_alive():
                self.controller_thread.join(timeout=2.0)
                
            self.save_application_state()
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
        finally:
            self.window.destroy()

    def save_application_state(self) -> None:
        """Save application state before closing."""
        try:
            state = {
                'total_sessions': getattr(self, 'total_sessions', 0) + 1
            }
            with open('app_state.json', 'w') as f:
                json.dump(state, f)
        except Exception as e:
            self.logger.error(f"Failed to save application state: {e}")


if __name__ == "__main__":
    try:
        check_dependencies()
        counter = ControllerCounter()
        counter.run()
    except Exception as e:
        print(f"\nError: {e}")
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
