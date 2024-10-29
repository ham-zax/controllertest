"""Button mapping configurations."""

from ..utils.constants import BUTTON_NAMES, ANALOG_MAPPING

def get_button_name(code: str) -> str:
    """Get the friendly name for a button code."""
    return BUTTON_NAMES.get(code, code)

def get_analog_mapping(code: str) -> tuple:
    """Get the stick and axis mapping for an analog input code."""
    return ANALOG_MAPPING.get(code, (None, None))

def get_dpad_direction(code: str, state: int) -> str:
    """Get the direction name for a D-pad input."""
    if code in BUTTON_NAMES and isinstance(BUTTON_NAMES[code], dict):
        return BUTTON_NAMES[code].get(state, "")
    return ""
