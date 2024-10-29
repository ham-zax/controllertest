"""Global constants used throughout the application."""

# Analog stick constants
ANALOG_MAX = 32767
ANALOG_THRESHOLD = 3000
ANALOG_DEADZONE = 0.1
TRIGGER_THRESHOLD = 100

# Button mappings
BUTTON_NAMES = {
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

# XUSB button mappings (evdev to vgamepad)
XUSB_BUTTON_MAPPING = {
    'BTN_NORTH': 'Y',
    'BTN_SOUTH': 'A',
    'BTN_EAST': 'B',
    'BTN_WEST': 'X',
    'BTN_TL': 'LEFT_SHOULDER',
    'BTN_TR': 'RIGHT_SHOULDER',
    'BTN_SELECT': 'BACK',
    'BTN_START': 'START',
    'BTN_MODE': 'GUIDE',
    'BTN_THUMBL': 'LEFT_THUMB',
    'BTN_THUMBR': 'RIGHT_THUMB'
}

# Analog stick mappings
ANALOG_MAPPING = {
    'ABS_X': ('LEFT', 'X'),
    'ABS_Y': ('LEFT', 'Y'),
    'ABS_RX': ('RIGHT', 'X'),
    'ABS_RY': ('RIGHT', 'Y')
}

# GUI constants
WINDOW_TITLE = "Xbox Controller Input Counter & Macro Recorder"
WINDOW_SIZE = "1200x800"
FONT_FAMILY = 'Arial'
FONT_SIZE_NORMAL = 12
FONT_SIZE_SMALL = 10
