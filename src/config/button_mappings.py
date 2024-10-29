"""Button mapping configurations"""
from typing import Dict

# Mapping from user-friendly Xbox names to XUSB_BUTTON names
XBOX_TO_XUSB = {
    'A': 'XUSB_GAMEPAD_A',
    'B': 'XUSB_GAMEPAD_B',
    'X': 'XUSB_GAMEPAD_X',
    'Y': 'XUSB_GAMEPAD_Y',
    'LB': 'XUSB_GAMEPAD_LEFT_SHOULDER',
    'RB': 'XUSB_GAMEPAD_RIGHT_SHOULDER',
    'Start': 'XUSB_GAMEPAD_START',
    'Back': 'XUSB_GAMEPAD_BACK',
    'LS': 'XUSB_GAMEPAD_LEFT_THUMB',
    'RS': 'XUSB_GAMEPAD_RIGHT_THUMB',
    'DPad Up': 'XUSB_GAMEPAD_DPAD_UP',
    'DPad Down': 'XUSB_GAMEPAD_DPAD_DOWN',
    'DPad Left': 'XUSB_GAMEPAD_DPAD_LEFT',
    'DPad Right': 'XUSB_GAMEPAD_DPAD_RIGHT',
}

# Reverse mapping from XUSB to Xbox names
XUSB_TO_XBOX = {v: k for k, v in XBOX_TO_XUSB.items()}

# Button codes mapping
BUTTON_CODES: Dict[int, str] = {
    1: 'A',
    2: 'B', 
    3: 'X',
    4: 'Y',
    5: 'LB',
    6: 'RB',
    7: 'Start',
    8: 'Back',
    9: 'LS',
    10: 'RS',
    11: 'DPad Up',
    12: 'DPad Down',
    13: 'DPad Left',
    14: 'DPad Right',
}
