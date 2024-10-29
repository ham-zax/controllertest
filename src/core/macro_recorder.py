"""Module for recording and playing back controller macros"""
import json
import threading
import time
from typing import Dict, List, Optional
import vgamepad
import logging
from src.config.button_mappings import XBOX_TO_XUSB

class MacroRecorder:
    """Class to handle macro recording and playback"""
    def __init__(self, gamepad):
        self.gamepad = gamepad
        self.recording = False
        self.playing = False
        self.current_macro: List[Dict] = []
        self.record_start_time: Optional[float] = None
        self.playback_thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger(__name__)
        self.saved_macros: Dict[str, List[Dict]] = {}
        self.button_assignments: Dict[str, str] = {}
        
        # Load saved macros from file if it exists
        try:
            with open('macros.json', 'r') as f:
                saved_data = json.load(f)
                self.saved_macros = saved_data.get('macros', {})
                self.button_assignments = saved_data.get('assignments', {})
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def start_recording(self):
        """Start recording a new macro"""
        self.recording = True
        self.current_macro = []
        self.record_start_time = time.time()
        self.logger.info("Started recording macro")

    def stop_recording(self, name: str = None):
        """Stop recording the current macro and optionally save it"""
        self.recording = False
        self.record_start_time = None
        
        if name and self.current_macro:
            self.saved_macros[name] = self.current_macro.copy()
            self._save_to_file()
            self.logger.info(f"Saved macro '{name}'")
        
        self.logger.info("Stopped recording macro")
        return self.current_macro

    def record_event(self, event_type: str, code: str, state: int, delay: float = 0.0):
        """Record a controller event"""
        if not self.recording:
            return
        
        self.current_macro.append({
            "type": event_type,
            "code": code,
            "state": state,
            "delay": delay
        })
        self.logger.debug(f"Recorded event: {event_type} {code} {state} delay={delay}")

    def play_macro(self, name: str = None, macro: List[Dict] = None):
        """Start playing back a macro"""
        if self.playing:
            return
            
        if name and name in self.saved_macros:
            macro = self.saved_macros[name]
        elif not macro:
            return
            
        self.playing = True
        self.playback_thread = threading.Thread(target=self._playback_thread, args=(macro,))
        self.playback_thread.start()
        self.logger.info("Started macro playback")

    def stop_playback(self):
        """Stop the current macro playback"""
        self.playing = False
        if self.playback_thread:
            self.playback_thread.join()
        self.logger.info("Stopped macro playback")

    def _playback_thread(self, macro: List[Dict]):
        """Thread function for playing back a macro"""
        if not macro:
            self.playing = False
            return

        try:
            for event in macro:
                if not self.playing:
                    break

                # Validate event structure
                if not isinstance(event, dict) or "type" not in event or "code" not in event or "state" not in event:
                    self.logger.error(f"Invalid event format: {event}")
                    continue

                # Handle delay
                delay = float(event.get("delay", 0))
                if delay > 0:
                    time.sleep(delay)

                try:
                    # Handle different event types
                    if event["type"] == "Key":
                        # Handle button press/release
                        button_name = event["code"].replace("BTN_", "")
                        xusb_button = XBOX_TO_XUSB.get(button_name)
                        if xusb_button:
                            button = getattr(vgamepad.XUSB_BUTTON, xusb_button)
                            if event["state"] == 1:
                                self.gamepad.press_button(button=button)
                            else:
                                self.gamepad.release_button(button=button)
                    
                    elif event["type"] == "Absolute":
                        # Handle analog inputs
                        if event["code"] == "ABS_X":
                            self.gamepad.left_joystick_float(x_value_float=event["state"]/32767.0, y_value_float=0)
                        elif event["code"] == "ABS_Y":
                            self.gamepad.left_joystick_float(x_value_float=0, y_value_float=event["state"]/32767.0)
                        elif event["code"] == "ABS_RX":
                            self.gamepad.right_joystick_float(x_value_float=event["state"]/32767.0, y_value_float=0)
                        elif event["code"] == "ABS_RY":
                            self.gamepad.right_joystick_float(x_value_float=0, y_value_float=event["state"]/32767.0)
                        elif event["code"] == "ABS_Z":
                            self.gamepad.left_trigger_float(value_float=event["state"]/255.0)
                        elif event["code"] == "ABS_RZ":
                            self.gamepad.right_trigger_float(value_float=event["state"]/255.0)

                    self.gamepad.update()

                except (AttributeError, ValueError) as e:
                    self.logger.error(f"Error processing event {event}: {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"Error during macro playback: {str(e)}")
        finally:
            self.playing = False
            self.logger.info("Finished macro playback")

    def delete_macro(self, name: str):
        """Delete a saved macro"""
        if name in self.saved_macros:
            del self.saved_macros[name]
            # Remove any button assignments for this macro
            self.button_assignments = {btn: macro for btn, macro in self.button_assignments.items() 
                                    if macro != name}
            self._save_to_file()
            self.logger.info(f"Deleted macro '{name}'")

    def adjust_timing(self, name: str, speed: float):
        """Adjust the timing of a saved macro"""
        if name not in self.saved_macros or speed <= 0:
            return
            
        macro = self.saved_macros[name]
        adjusted_macro = []
        
        for event in macro:
            adjusted_event = event.copy()
            if "delay" in adjusted_event:
                adjusted_event["delay"] = event["delay"] / speed
            adjusted_macro.append(adjusted_event)
            
        self.saved_macros[name] = adjusted_macro
        self._save_to_file()
        self.logger.info(f"Adjusted timing for macro '{name}' with speed {speed}")

    def assign_macro(self, name: str, button: str):
        """Assign a macro to a button"""
        if name in self.saved_macros:
            self.button_assignments[button] = name
            self._save_to_file()
            self.logger.info(f"Assigned macro '{name}' to button {button}")

    def _save_to_file(self):
        """Save macros and button assignments to file"""
        try:
            with open('macros.json', 'w') as f:
                json.dump({
                    'macros': self.saved_macros,
                    'assignments': self.button_assignments
                }, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving macros to file: {str(e)}")
