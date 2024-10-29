"""Macro recording and playback functionality."""

import json
import threading
import time
import vgamepad

class MacroRecorder:
    def __init__(self):
        self.recording = False
        self.current_macro = []
        self.saved_macros = {}
        self.macro_assignments = {}
        self.playback_active = False
        self.gamepad = vgamepad.VX360Gamepad()
        self.loop_macro = False
        self.load_macros()
        self.create_stick_x_macro()

    def create_stick_x_macro(self):
        """Create a default stick south + X macro."""
        macro = [
            {'type': 'Absolute', 'code': 'ABS_Y', 'state': 32767, 'delay': 0},
            {'type': 'Absolute', 'code': 'ABS_Y', 'state': 32767, 'delay': 0.1},
            {'type': 'Key', 'code': 'BTN_WEST', 'state': 1, 'delay': 0.1},
            {'type': 'Key', 'code': 'BTN_WEST', 'state': 0, 'delay': 0.15},
            {'type': 'Absolute', 'code': 'ABS_Y', 'state': 0, 'delay': 0.15}
        ]
        self.saved_macros['stick_south_x'] = macro
        self.macro_assignments['BTN_TR'] = 'stick_south_x'
        self.save_macros()

    def record_event(self, ev_type, code, state, timestamp):
        """Record a controller event."""
        if self.recording:
            delay = 0
            if self.current_macro:
                delay = timestamp - self.current_macro[-1]['timestamp']
            self.current_macro.append({
                'type': ev_type,
                'code': code,
                'state': state,
                'delay': delay,
                'timestamp': timestamp
            })

    def stop_recording(self, name=None):
        """Stop recording and optionally save the macro."""
        if not self.recording:
            return "Not currently recording"
        
        self.recording = False
        if not name or not self.current_macro:
            self.current_macro = []
            return "Recording cancelled"
        
        processed_macro = []
        for event in self.current_macro:
            processed_macro.append({
                'type': event['type'],
                'code': event['code'],
                'state': event['state'],
                'delay': event['delay']
            })
        
        self.saved_macros[name] = processed_macro
        self.save_macros()
        self.current_macro = []
        return f"Saved macro as '{name}'"

    def _playback_thread(self, events):
        """Thread function for macro playback."""
        while self.playback_active:
            for event in events:
                if not self.playback_active:
                    break
                
                time.sleep(event['delay'])
                
                if event['type'] == 'Key':
                    if event['state']:
                        self.gamepad.press_button(button=getattr(vgamepad.XUSB_BUTTON, event['code']))
                    else:
                        self.gamepad.release_button(button=getattr(vgamepad.XUSB_BUTTON, event['code']))
                elif event['type'] == 'Absolute':
                    if event['code'] == 'ABS_X':
                        self.gamepad.left_joystick_float(x_value_float=event['state'] / 32767.0, y_value_float=0.0)
                    elif event['code'] == 'ABS_Y':
                        self.gamepad.left_joystick_float(x_value_float=0.0, y_value_float=event['state'] / 32767.0)
                
                self.gamepad.update()
            
            if not self.loop_macro:
                self.playback_active = False

    def play_macro(self, name, loop=False):
        """Play back a recorded macro."""
        if name not in self.saved_macros:
            return f"Macro '{name}' not found"
        
        self.playback_active = True
        self.loop_macro = loop
        events = self.saved_macros[name]
        
        thread = threading.Thread(target=self._playback_thread, args=(events,))
        thread.start()
        return f"Playing macro '{name}' {'(looping)' if loop else ''}"

    def stop_playback(self):
        """Stop macro playback."""
        self.playback_active = False
        self.loop_macro = False
        return "Stopped macro playback"

    def save_macros(self):
        """Save macros and assignments to file."""
        try:
            data = {
                'macros': self.saved_macros,
                'assignments': self.macro_assignments
            }
            with open('macros.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving macros: {e}")

    def load_macros(self):
        """Load macros and assignments from file."""
        try:
            with open('macros.json', 'r') as f:
                data = json.load(f)
                self.saved_macros = data.get('macros', {})
                self.macro_assignments = data.get('assignments', {})
        except FileNotFoundError:
            self.saved_macros = {}
            self.macro_assignments = {}
        except Exception as e:
            print(f"Error loading macros: {e}")
            self.saved_macros = {}
            self.macro_assignments = {}
