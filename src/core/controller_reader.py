"""Controller input reading and processing."""

import logging
import time
from datetime import datetime
from inputs import get_gamepad
import threading
import queue

class ControllerReader:
    def __init__(self, input_handler):
        self.logger = logging.getLogger('ControllerReader')
        self.running = True
        self.input_handler = input_handler
        self._stop_event = threading.Event()
        self._event_queue = queue.Queue()
        self._reader_thread = None
        
    def _read_events(self):
        """Background thread to read gamepad events."""
        while not self._stop_event.is_set():
            try:
                events = get_gamepad()
                for event in events:
                    if self._stop_event.is_set():
                        break
                    self._event_queue.put(event)
            except Exception as e:
                if not self._stop_event.is_set():
                    self.logger.error(f"Controller error: {e}")
                    time.sleep(0.1)
        
    def start(self):
        """Start reading controller inputs."""
        self._reader_thread = threading.Thread(target=self._read_events)
        self._reader_thread.daemon = True
        self._reader_thread.start()
        
        reconnect_delay = 1
        max_reconnect_delay = 30
        
        while not self._stop_event.is_set():
            try:
                # Use timeout to check stop flag frequently
                try:
                    event = self._event_queue.get(timeout=0.1)
                    reconnect_delay = 1
                    self.input_handler.process_event(event, datetime.now())
                except queue.Empty:
                    continue
                    
            except Exception as e:
                if not self._stop_event.is_set():
                    self.logger.error(f"Processing error: {e}")
                    self.input_handler.on_controller_disconnect()
                    time.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)
    
    def stop(self):
        """Stop reading controller inputs."""
        self._stop_event.set()
        self.running = False
        # Clear the queue to prevent blocking
        while not self._event_queue.empty():
            try:
                self._event_queue.get_nowait()
            except queue.Empty:
                break
        if self._reader_thread and self._reader_thread.is_alive():
            self._reader_thread.join(timeout=1.0)
