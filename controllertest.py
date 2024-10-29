"""Xbox controller input counter, macro recorder, and signal modifier."""

import sys
import json
from pathlib import Path
import time
from datetime import datetime
import threading
import math
from threading import Lock
import logging
import tkinter as tk
from tkinter import ttk

def check_dependencies():
    """Check if all required dependencies are installed."""
    missing_deps = []
    try:
        import tkinter as tk
    except ImportError:
        missing_deps.append("tkinter")
    
    try:
        from inputs import get_gamepad
    except ImportError:
        missing_deps.append("inputs")
    
    if missing_deps:
        print("Error: Missing required dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nPlease install missing dependencies:")
        if "inputs" in missing_deps:
            print("  pip install inputs==0.5")
        if "tkinter" in missing_deps:
            print("  Tkinter usually comes with Python. Please ensure you have Python installed correctly.")
        sys.exit(1)

# Check dependencies before importing
check_dependencies()

from inputs import get_gamepad
import vgamepad

class MacroRecorder:
    """Records and plays back controller input sequences."""
    
    def __init__(self):
        self.recording = False
        self.current_macro = []
        self.saved_macros = {}
        self.playback_active = False
        self.gamepad = vgamepad.VX360Gamepad()
        self.load_macros()

    def start_recording(self):
        """Start recording a new macro."""
        self.current_macro = []
        self.recording = True
        return "Started recording new macro"

    def stop_recording(self, name):
        """Stop recording and save the macro."""
        self.recording = False
        if name and self.current_macro:
            self.saved_macros[name] = self.current_macro
            self.save_macros()
            return f"Saved macro '{name}' with {len(self.current_macro)} events"
        return "No macro recorded"

    def record_event(self, event_type, code, state, timestamp):
        """Record a controller event."""
        if self.recording:
            self.current_macro.append({
                'type': event_type,
                'code': code,
                'state': state,
                'delay': timestamp
            })

    def play_macro(self, name):
        """Play back a recorded macro."""
        if name not in self.saved_macros:
            return f"Macro '{name}' not found"
        
        self.playback_active = True
        events = self.saved_macros[name]
        
        # Create a thread for playback
        thread = threading.Thread(target=self._playback_thread, args=(events,))
        thread.start()
        return f"Playing macro '{name}'"

    def _playback_thread(self, events):
        """Thread that handles macro playback."""
        last_time = None
        
        for event in events:
            if not self.playback_active:
                break
                
            if last_time is not None:
                # Wait for the recorded delay between events
                time.sleep(event['delay'] - last_time)
            
            # Map event to virtual gamepad
            if event['type'] == 'Key':
                if event['code'] == 'BTN_NORTH':
                    self.gamepad.press_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_Y) if event['state'] else self.gamepad.release_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_Y)
                elif event['code'] == 'BTN_SOUTH':
                    self.gamepad.press_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A) if event['state'] else self.gamepad.release_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_A)
                elif event['code'] == 'BTN_EAST':
                    self.gamepad.press_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B) if event['state'] else self.gamepad.release_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_B)
                elif event['code'] == 'BTN_WEST':
                    self.gamepad.press_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_X) if event['state'] else self.gamepad.release_button(vgamepad.XUSB_BUTTON.XUSB_GAMEPAD_X)
            
            self.gamepad.update()
            last_time = event['delay']
        
        self.playback_active = False

    def stop_playback(self):
        """Stop macro playback."""
        self.playback_active = False
        return "Stopped macro playback"

    def save_macros(self):
        """Save macros to file."""
        try:
            with open('macros.json', 'w') as f:
                json.dump(self.saved_macros, f)
        except Exception as e:
            print(f"Error saving macros: {e}")

    def load_macros(self):
        """Load macros from file."""
        try:
            with open('macros.json', 'r') as f:
                self.saved_macros = json.load(f)
        except FileNotFoundError:
            self.saved_macros = {}
        except Exception as e:
            print(f"Error loading macros: {e}")
            self.saved_macros = {}

class ControllerCounter:
    """
    A class to track, modify and record Xbox controller inputs with a GUI interface.
    """

    def __init__(self):
        """Initialize the controller counter and setup the GUI."""
        # Setup logging first
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing ControllerCounter")

        try:
            # Initialize macro recorder
            self.macro_recorder = MacroRecorder()

            # Test gamepad availability
            try:
                get_gamepad()
            except Exception as e:
                self.logger.error("No gamepad detected")
                raise RuntimeError("No gamepad detected. Please connect an Xbox controller and try again.") from e

            self.window = tk.Tk()
            self.window.title("Xbox Controller Input Counter & Macro Recorder")
            self.window.geometry("1000x800")
            
            # Add macro control frame
            self.setup_macro_controls()
            
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

            # Timer label
            self.timer_label = tk.Label(
                current_frame,
                text="Time: 0s",
                font=('Arial', 12)
            )
            self.timer_label.pack(pady=5)
            self.start_time = time.time()
            self.update_timer()

            # Analog sticks frame
            analog_frame = tk.LabelFrame(
                self.window,
                text="Analog Sticks",
                padx=10,
                pady=10
            )
            analog_frame.pack(fill="x", padx=10, pady=5)

            self.left_stick_label = tk.Label(
                analog_frame,
                text="Left Stick: Center",
                font=('Arial', 12)
            )
            self.left_stick_label.pack(pady=5)

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
            self.analog_threshold = 3000
            self.analog_max = 32768
            self.analog_deadzone = 0.1
            
            # Button state tracking
            self.button_states = {}
            
            # Trigger thresholds
            self.trigger_threshold = 100
            
            # Debug information
            self.debug_info = {}
            
            # Flag for thread control
            self.running = True
            
            # Start controller input thread
            self.controller_thread = threading.Thread(target=self.read_controller)
            self.controller_thread.daemon = True
            self.controller_thread.start()
            
            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.gui_lock = Lock()

        except Exception as e:
            self.logger.error(f"Failed to initialize ControllerCounter: {e}")
            if hasattr(self, 'window'):
                self.window.destroy()
            raise

    def update_timer(self):
        """Update the timer display every second."""
        if self.running:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {elapsed}s")
            self.window.after(1000, self.update_timer)

    def setup_macro_controls(self):
        """Setup the macro recording and playback controls."""
        macro_frame = tk.LabelFrame(
            self.window,
            text="Macro Controls",
            padx=10,
            pady=10
        )
        macro_frame.pack(fill="x", padx=10, pady=5)

        # Macro name entry
        self.macro_name = tk.StringVar()
        name_frame = tk.Frame(macro_frame)
        name_frame.pack(fill="x", pady=5)
        
        tk.Label(name_frame, text="Macro Name:").pack(side=tk.LEFT, padx=5)
        tk.Entry(name_frame, textvariable=self.macro_name).pack(side=tk.LEFT, fill="x", expand=True, padx=5)

        # Control buttons
        button_frame = tk.Frame(macro_frame)
        button_frame.pack(fill="x", pady=5)
        
        tk.Button(
            button_frame,
            text="Start Recording",
            command=self.start_macro_recording
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Stop Recording",
            command=self.stop_macro_recording
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Play Macro",
            command=self.play_selected_macro
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Stop Playback",
            command=self.stop_macro_playback
        ).pack(side=tk.LEFT, padx=5)

        # Macro list
        list_frame = tk.Frame(macro_frame)
        list_frame.pack(fill="x", pady=5)
        
        tk.Label(list_frame, text="Saved Macros:").pack(anchor="w")
        
        self.macro_listbox = tk.Listbox(list_frame, height=3)
        self.macro_listbox.pack(fill="x", pady=5)
        self.update_macro_list()

    def setup_logging(self):
        """Configure logging system with file and console output."""
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            logging.basicConfig(
                level=logging.WARNING,  # Changed to WARNING to reduce logs
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_dir / "controller_counter.log"),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        except Exception as e:
            print(f"Failed to setup logging: {e}")
            raise

    def update_macro_list(self):
        """Update the list of saved macros."""
        self.macro_listbox.delete(0, tk.END)
        for name in self.macro_recorder.saved_macros:
            self.macro_listbox.insert(tk.END, name)

    def start_macro_recording(self):
        """Start recording a new macro."""
        result = self.macro_recorder.start_recording()
        self.add_to_history("Macro Recorder", True, None, result)

    def stop_macro_recording(self):
        """Stop recording the current macro."""
        name = self.macro_name.get()
        if name:
            result = self.macro_recorder.stop_recording(name)
            self.add_to_history("Macro Recorder", False, None, result)
            self.update_macro_list()
            self.macro_name.set("")
        else:
            self.add_to_history("Macro Recorder", False, None, "Please enter a macro name")

    def play_selected_macro(self):
        """Play the selected macro."""
        selection = self.macro_listbox.curselection()
        if selection:
            name = self.macro_listbox.get(selection[0])
            result = self.macro_recorder.play_macro(name)
            self.add_to_history("Macro Recorder", True, None, result)
        else:
            self.add_to_history("Macro Recorder", False, None, "Please select a macro to play")

    def stop_macro_playback(self):
        """Stop macro playback."""
        result = self.macro_recorder.stop_playback()
        self.add_to_history("Macro Recorder", False, None, result)

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
