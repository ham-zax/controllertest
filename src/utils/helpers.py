"""Helper functions used across the application."""

import json
import math
from datetime import datetime

def save_json(data: dict, filename: str) -> None:
    """Save data to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving to {filename}: {e}")

def load_json(filename: str) -> dict:
    """Load data from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return {}

def get_analog_direction(x: int, y: int, max_value: int, deadzone: float) -> tuple[str, float]:
    """Convert analog stick coordinates to direction and magnitude."""
    x_norm = x / max_value
    y_norm = -y / max_value

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

def format_timestamp(timestamp: datetime = None) -> str:
    """Format a timestamp for display."""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%H:%M:%S.%f")[:-3]
