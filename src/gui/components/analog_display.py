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

    def update_stick(self, stick, x, y):
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

    def get_analog_direction(self, x, y):
        """Convert analog stick coordinates to direction and magnitude."""
        analog_max = 32767
        deadzone = 0.1
        
        x_norm = x / analog_max
        y_norm = -y / analog_max

        magnitude = math.sqrt(x_norm**2 + y_norm**2)
        
        if magnitude < deadzone:
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

def setup_analog_display(parent):
    """Create and return an AnalogDisplay instance."""
    return AnalogDisplay(parent)
