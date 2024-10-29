"""Input processing and state management."""

import math
from datetime import datetime

class InputProcessor:
    def __init__(self, gui_handler):
        self.gui_handler = gui_handler
        self.analog_max = 32767
        self.analog_threshold = 3000
        self.analog_deadzone = 0.1
        self.trigger_threshold = 100
        self.button_states = {}
        self.analog_states = {
            'LEFT': {'X': 0, 'Y': 0},
            'RIGHT': {'X': 0, 'Y': 0}
        }
        self.setup_mappings()

    def setup_mappings(self):
        """Setup button and analog mappings."""
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

    def get_analog_direction(self, x: int, y: int) -> tuple[str, float]:
        """Convert analog stick coordinates to direction and magnitude."""
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

    def process_event(self, event, timestamp):
        """Process a controller input event."""
        self.gui_handler.update_debug_info(event)

        if event.ev_type == 'Key':
            if event.code in self.button_names:
                button_name = self.button_names[event.code]
                self.gui_handler.handle_input(button_name, bool(event.state), timestamp, event)
        
        elif event.ev_type == 'Absolute':
            if event.code in self.analog_mapping:
                stick, axis = self.analog_mapping[event.code]
                self.analog_states[stick][axis] = event.state
                
                x = self.analog_states[stick]['X']
                y = self.analog_states[stick]['Y']
                if abs(x) > self.analog_threshold or abs(y) > self.analog_threshold:
                    self.gui_handler.update_analog_display(stick, x, y)
            
            elif event.code in ['ABS_RZ', 'ABS_Z']:
                button_name = self.button_names[event.code]
                is_pressed = event.state > self.trigger_threshold
                
                current_state = self.button_states.get(button_name, False)
                if current_state != is_pressed:
                    self.button_states[button_name] = is_pressed
                    self.gui_handler.handle_input(button_name, is_pressed, timestamp, event)
            
            elif event.code in self.button_names and event.state in self.button_names[event.code]:
                direction = self.button_names[event.code][event.state]
                self.gui_handler.handle_input(direction, True, timestamp, event)
