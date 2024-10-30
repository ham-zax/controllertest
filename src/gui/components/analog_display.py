"""Analog stick display component."""

import tkinter as tk
from tkinter import ttk
import math

class AnalogDisplay:
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Analog Sticks", padding=10)
        self.frame.pack(fill="x", pady=5)
        
        self.left_stick_label = ttk.Label(
            self.frame,
            text="Left Stick: Center",
            font=('Arial', 12)
        )
        self.left_stick_label.pack(pady=5)
        
        self.right_stick_label = ttk.Label(
            self.frame,
            text="Right Stick: Center",
            font=('Arial', 12)
        )
        self.right_stick_label.pack(pady=5)

        self.direction_map = {
            "North": "↓",
            "South": "↑",
            "East": "→",
            "West": "←",
            "Northeast": "↘",
            "Northwest": "↙",
            "Southeast": "↗",
            "Southwest": "↖",
            "up": "↑",
            "down": "↓",
            "left": "←",
            "right": "→",
            "Up": "↑",
            "Down": "↓",
            "Left": "←",
            "Right": "→",
            "UpLeft": "↖",
            "UpRight": "↗",
            "DownLeft": "↙",
            "DownRight": "↘",
            "Center": "●"
        }

    def update_stick(self, stick, x, y):
        """Update the display for analog stick position."""
        direction, magnitude = self.get_analog_direction(x, y)
        simple_direction = self.direction_map.get(direction, direction)
        
        if stick == 'LEFT':
            if magnitude == 0:
                self.left_stick_label.config(text="Left Stick: Center")
            else:
                self.left_stick_label.config(
                    text=f"Left Stick: {simple_direction} ({magnitude}%)"
                )
        else:
            if magnitude == 0:
                self.right_stick_label.config(text="Right Stick: Center")
            else:
                self.right_stick_label.config(
                    text=f"Right Stick: {simple_direction} ({magnitude}%)"
                )

    def get_analog_direction(self, x, y):
        """Convert analog stick coordinates to direction and magnitude."""
        analog_max = 32767
        deadzone = 0.2  # Increased deadzone
        
        x_norm = x / analog_max
        y_norm = -y / analog_max

        magnitude = math.sqrt(x_norm**2 + y_norm**2)
        
        if magnitude < deadzone:
            return "Center", 0

        # Normalize magnitude to account for deadzone
        adjusted_magnitude = (magnitude - deadzone) / (1 - deadzone)
        magnitude_percent = min(100, max(0, round(adjusted_magnitude * 100)))

        angle = math.degrees(math.atan2(y_norm, x_norm))
        if angle < 0:
            angle += 360

        directions = [
            "East", "Northeast", "North", "Northwest",
            "West", "Southwest", "South", "Southeast"
        ]
        index = int((angle + 22.5) / 45) % 8
        direction = directions[index]

        return direction, magnitude_percent

def setup_analog_display(parent):
    """Create and return an AnalogDisplay instance."""
    return AnalogDisplay(parent)
