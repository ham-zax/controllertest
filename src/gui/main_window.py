"""Main application window and GUI setup."""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import logging
import json
import threading
import time
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
        
        self.running = True
        self.press_count = 0
        self.last_reset = 0
        self.last_count = 0
        self.debug_info = {}
        
        # Initialize controller components before GUI
        self.setup_controller()
        self.setup_gui()
        
        # Set up window close handler
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

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
        self.macro_recorder = MacroRecorder()
        self.input_processor = InputProcessor(self)
        self.controller_reader = ControllerReader(self.input_processor)
        
        # Start controller thread
        self.controller_thread = threading.Thread(target=self.controller_reader.start)
        self.controller_thread.daemon = True
        self.controller_thread.start()

    def setup_gui(self):
        """Setup the main GUI components."""
        # Create main columns
        left_column = ttk.Frame(self.window)
        left_column.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        middle_column = ttk.Frame(self.window)
        middle_column.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        right_column = ttk.Frame(self.window)
        right_column.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        # Setup components
        self.input_status = setup_input_status(left_column)
        self.counter = setup_counter(left_column)
        self.analog_display = setup_analog_display(middle_column)
        self.debug_panel = setup_debug_info(middle_column)
        self.macro_controls = setup_macro_controls(right_column, self.macro_recorder)
        self.history_panel = setup_history(right_column)

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
            self.controller_reader.stop()
            
            if self.controller_thread.is_alive():
                self.controller_thread.join(timeout=2.0)
                
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
        self.analog_display.update_stick(stick, x, y)