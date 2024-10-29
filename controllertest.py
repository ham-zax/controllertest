import tkinter as tk
from inputs import get_gamepad
from time import time
import threading
from datetime import datetime

class ControllerCounter:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Xbox Controller Input Counter")
        self.window.geometry("800x600")
        
        # Current input frame
        current_frame = tk.LabelFrame(self.window, text="Current Input Status", padx=10, pady=10)
        current_frame.pack(fill="x", padx=10, pady=5)
        
        self.current_input_label = tk.Label(current_frame, text="No input", font=('Arial', 12))
        self.current_input_label.pack(pady=5)
        
        # Counter frame
        counter_frame = tk.LabelFrame(self.window, text="1-Second Counter", padx=10, pady=10)
        counter_frame.pack(fill="x", padx=10, pady=5)
        
        self.counter_label = tk.Label(counter_frame, 
                                    text="Current count (1s): 0", 
                                    font=('Arial', 12))
        self.counter_label.pack(pady=5)
        
        self.last_count_label = tk.Label(counter_frame, 
                                       text="Previous count: 0", 
                                       font=('Arial', 12))
        self.last_count_label.pack(pady=5)
        
        # Input history frame
        history_frame = tk.LabelFrame(self.window, text="Input History", padx=10, pady=10)
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
            'ABS_HAT0Y': {-1: 'D-Pad Up', 1: 'D-Pad Down'},
            'ABS_HAT0X': {-1: 'D-Pad Left', 1: 'D-Pad Right'}
        }
        
        # Flag for thread control
        self.running = True
        
        # Start controller input thread
        self.controller_thread = threading.Thread(target=self.read_controller)
        self.controller_thread.daemon = True
        self.controller_thread.start()
    
    def add_to_history(self, input_name):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        history_entry = f"[{timestamp}] {input_name}\n"
        
        # Add to text widget and auto-scroll
        self.history_text.insert(tk.END, history_entry)
        self.history_text.see(tk.END)
    
    def update_counter(self):
        current_time = time()
        
        # If more than a second has passed
        if current_time - self.last_reset >= 1:
            # Store the last count before resetting
            self.last_count = self.press_count
            self.last_count_label.config(text=f"Previous count: {self.last_count}")
            
            # Reset counter
            self.press_count = 0
            self.last_reset = current_time
        
        self.press_count += 1
        self.counter_label.config(text=f"Current count (1s): {self.press_count}")
    
    def read_controller(self):
        while self.running:
            try:
                events = get_gamepad()
                for event in events:
                    # Handle button presses
                    if event.ev_type == 'Key' and event.state == 1:
                        if event.code in self.button_names:
                            button_name = self.button_names[event.code]
                            self.window.after(0, lambda b=button_name: self.handle_input(b))
                    
                    # Handle D-pad
                    elif event.ev_type == 'Absolute':
                        if event.code in self.button_names and event.state in self.button_names[event.code]:
                            direction = self.button_names[event.code][event.state]
                            self.window.after(0, lambda d=direction: self.handle_input(d))
            except Exception as e:
                self.window.after(0, lambda: self.current_input_label.config(
                    text="Controller disconnected or error occurred"))
    
    def handle_input(self, input_name):
        # Update current input display
        self.current_input_label.config(text=f"Current Input: {input_name}")
        
        # Add to history
        self.add_to_history(input_name)
        
        # Update counter
        self.update_counter()
    
    def run(self):
        try:
            self.window.mainloop()
        finally:
            self.running = False

if __name__ == "__main__":
    counter = ControllerCounter()
    counter.run()
