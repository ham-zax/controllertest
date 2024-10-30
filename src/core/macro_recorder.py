"""Module for recording and playing back controller macros"""
import json
import threading
import time
from typing import Dict, List, Optional
import vgamepad
import logging
from datetime import datetime
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
        self.history_panel = None  # Will be set by MainWindow
        
        # Load saved macros from file if it exists
        try:
            with open('macros.json', 'r') as f:
                saved_data = json.load(f)
                self.saved_macros = saved_data.get('macros', {})
                self.button_assignments = saved_data.get('assignments', {})
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def set_history_panel(self, history_panel):
        """Set the history panel reference for logging playback events"""
        self.history_panel = history_panel

    def start_recording(self):
        """Start recording a new macro"""
        if self.recording:
            return False
        self.recording = True
        self.current_macro = []
        self.record_start_time = time.time()
        self.logger.info("Started recording macro")
        if self.history_panel:
            self.history_panel.add_macro_event("record_start", 
                details="Started recording new macro")
        return True

    def stop_recording(self, name: str = None):
        """Stop recording the current macro and optionally save it"""
        if not self.recording:
            return None
            
        self.recording = False
        self.record_start_time = None
        
        if name and self.current_macro:
            self.saved_macros[name] = self.current_macro.copy()
            self._save_to_file()
            self.logger.info(f"Saved macro '{name}'")
            if self.history_panel:
                self.history_panel.add_macro_event("record_end", 
                    details=f"Saved macro '{name}' with {len(self.current_macro)} events")
        else:
            if self.history_panel:
                self.history_panel.add_macro_event("record_end", 
                    details="Recording stopped without saving")
        
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
            return False
            
        if name and name in self.saved_macros:
            macro = self.saved_macros[name]
            self.logger.info(f"Starting playback of macro '{name}' with {len(macro)} events")
            if self.history_panel:
                self.history_panel.add_macro_event("playback_start", 
                    details=f"Playing macro '{name}' ({len(macro)} events)")
        elif macro:
            self.logger.info(f"Starting playback of unnamed macro with {len(macro)} events")
            if self.history_panel:
                self.history_panel.add_macro_event("playback_start", 
                    details=f"Playing unnamed macro ({len(macro)} events)")
        else:
            return False
            
        self.playing = True
        self.playback_thread = threading.Thread(target=self._playback_thread, args=(macro,))
        self.playback_thread.start()

    def stop_playback(self):
        """Stop the current macro playback"""
        if not self.playing:
            return
        self.playing = False
        if self.playback_thread:
            self.playback_thread.join()
        self.logger.info("Stopped macro playback")
        if self.history_panel:
            self.history_panel.add_macro_event("playback_end", 
                details="Macro playback stopped")

    def _playback_thread(self, macro: List[Dict]):
        """Thread function for playing back a macro"""
        if not macro:
            self.playing = False
            return

        try:
            for event in macro:
                if not self.playing:
                    break

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
                                if self.history_panel:
                                    self.history_panel.add_entry(button_name, True, datetime.now())
                            else:
                                self.gamepad.release_button(button=button)
                                if self.history_panel:
                                    self.history_panel.add_entry(button_name, False, datetime.now())
                    
                    elif event["type"] == "Absolute":
                        # Handle analog inputs
                        if event["code"] == "ABS_X":
                            value = event["state"]/32767.0
                            self.gamepad.left_joystick_float(x_value_float=value, y_value_float=0)
                            if self.history_panel:
                                direction = "right" if value > 0 else "left"
                                magnitude = abs(int(value * 100))
                                self.history_panel.add_entry("LEFT", True, datetime.now(), (direction, magnitude))
                        elif event["code"] == "ABS_Y":
                            value = event["state"]/32767.0
                            self.gamepad.left_joystick_float(x_value_float=0, y_value_float=value)
                            if self.history_panel:
                                direction = "down" if value > 0 else "up"
                                magnitude = abs(int(value * 100))
                                self.history_panel.add_entry("LEFT", True, datetime.now(), (direction, magnitude))
                        elif event["code"] == "ABS_RX":
                            value = event["state"]/32767.0
                            self.gamepad.right_joystick_float(x_value_float=value, y_value_float=0)
                            if self.history_panel:
                                direction = "right" if value > 0 else "left"
                                magnitude = abs(int(value * 100))
                                self.history_panel.add_entry("RIGHT", True, datetime.now(), (direction, magnitude))
                        elif event["code"] == "ABS_RY":
                            value = event["state"]/32767.0
                            self.gamepad.right_joystick_float(x_value_float=0, y_value_float=value)
                            if self.history_panel:
                                direction = "down" if value > 0 else "up"
                                magnitude = abs(int(value * 100))
                                self.history_panel.add_entry("RIGHT", True, datetime.now(), (direction, magnitude))
                        elif event["code"] == "ABS_Z":
                            value = event["state"]/255.0
                            self.gamepad.left_trigger_float(value_float=value)
                            if self.history_panel:
                                self.history_panel.add_entry("LT", True, datetime.now())
                        elif event["code"] == "ABS_RZ":
                            value = event["state"]/255.0
                            self.gamepad.right_trigger_float(value_float=value)
                            if self.history_panel:
                                self.history_panel.add_entry("RT", True, datetime.now())

                    self.gamepad.update()

                except (AttributeError, ValueError) as e:
                    self.logger.error(f"Error processing event: {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"Error during macro playback: {str(e)}")
        finally:
            self.playing = False

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
