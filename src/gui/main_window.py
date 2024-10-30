"""Main application window and GUI setup."""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import logging
import json
import time
import vgamepad
from src.core.controller_reader import ControllerReader
from src.core.input_processor import InputProcessor
from src.core.macro_recorder import MacroRecorder
from src.gui.components.input_status import setup_input_status
from src.gui.components.counter import setup_counter
from src.gui.components.analog_display import setup_analog_display
from src.gui.components.debug_panel import setup_debug_info
from src.gui.components.macro_controls import setup_macro_controls
from src.gui.components.history_panel import setup_history

class MainWindow:
    def __init__(self):
        """Initialize the main application window."""
        self.setup_logging()
        self.logger = logging.getLogger('MainWindow')
        
        self.window = tk.Tk()
        self.window.title("Xbox Controller Input Counter & Macro Recorder")
        self.window.geometry("1200x800")
        self.window.minsize(1000, 600)  # Set minimum window size
        
        self.running = True
        self.press_count = 0
        self.last_reset = 0
        self.last_count = 0
        self.debug_info = {}
        
        # Initialize controller components before GUI
        self.setup_controller()
        self.setup_gui()
        
        # Connect history panel to macro recorder
        self.macro_recorder.set_history_panel(self.history_panel)
        
        # Set up window close handler
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Schedule controller polling
        self.schedule_controller_poll()

    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/controller_counter.log'),
                logging.StreamHandler()
            ]
        )

    def setup_controller(self):
        """Setup controller input handling."""
        # Create virtual gamepad for macro playback
        virtual_gamepad = vgamepad.VX360Gamepad()
        self.macro_recorder = MacroRecorder(virtual_gamepad)
        self.input_processor = InputProcessor(self)
        self.controller_reader = ControllerReader(self.input_processor)

    def schedule_controller_poll(self):
        """Schedule the next controller poll."""
        if self.running:
            try:
                # Process any pending controller events
                self.controller_reader.start()
                # Schedule next poll
                self.window.after(16, self.schedule_controller_poll)  # ~60Hz polling
            except Exception as e:
                self.logger.error(f"Error polling controller: {e}")
                # Retry after delay on error
                self.window.after(1000, self.schedule_controller_poll)

    def setup_gui(self):
        """Setup the main GUI components."""
        # Create main container with grid
        self.main_container = ttk.Frame(self.window)
        self.main_container.pack(fill="both", expand=True)
        
        # Configure grid weights
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(2, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Create columns as frames
        left_column = ttk.Frame(self.main_container)
        left_column.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        middle_column = ttk.Frame(self.main_container)
        middle_column.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        right_column = ttk.Frame(self.main_container)
        right_column.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        # Setup components
        self.input_status = setup_input_status(left_column)
        self.counter = setup_counter(left_column)
        self.analog_display = setup_analog_display(middle_column)
        self.debug_panel = setup_debug_info(middle_column)
        self.history_panel = setup_history(right_column)
        self.macro_controls = setup_macro_controls(right_column, self.macro_recorder)

    def run(self):
        """Start the application main loop."""
        try:
            self.window.mainloop()
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
        finally:
            self.running = False

    def on_closing(self):
        """Handle application shutdown gracefully."""
        try:
            self.logger.info("Application shutting down...")
            self.running = False
            self.save_application_state()
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
        finally:
            self.window.destroy()

    def save_application_state(self):
        """Save application state before closing."""
        try:
            state = {
                'total_sessions': getattr(self, 'total_sessions', 0) + 1
            }
            with open('app_state.json', 'w') as f:
                json.dump(state, f)
        except Exception as e:
            self.logger.error(f"Failed to save application state: {e}")

    def handle_input(self, input_name, is_pressed, timestamp, event=None):
        """Process and display a controller input event."""
        try:
            if not isinstance(input_name, str):
                raise ValueError(f"Invalid input_name type: {type(input_name)}")
            if not isinstance(is_pressed, bool):
                raise ValueError(f"Invalid is_pressed type: {type(is_pressed)}")
            
            input_name = str(input_name)[:50]
            
            self.input_status.update_input(input_name, is_pressed)
            self.history_panel.add_entry(input_name, is_pressed, timestamp)
            
            if is_pressed:
                self.counter.update()
            
            if event and self.macro_recorder.recording:
                self.macro_recorder.record_event(
                    event.ev_type,
                    event.code,
                    event.state,
                    time.time()
                )
                
        except Exception as e:
            self.logger.error(f"Error handling input: {e}")

    def update_debug_info(self, event):
        """Update debug information display."""
        self.debug_panel.update_info(event)

    def update_analog_display(self, stick, x, y):
        """Update analog stick display."""
        direction, magnitude = self.analog_display.get_analog_direction(x, y)
        self.analog_display.update_stick(stick, x, y)
        # Add analog movement to history
        self.history_panel.add_entry(stick, True, datetime.now(), (direction, magnitude))
