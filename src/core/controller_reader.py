"""Controller input reading and processing."""

import logging
import time
from datetime import datetime
from inputs import get_gamepad

class ControllerReader:
    def __init__(self, input_handler):
        self.logger = logging.getLogger('ControllerReader')
        self.running = True
        self.input_handler = input_handler
        
    def start(self):
        """Start reading controller inputs."""
        reconnect_delay = 1
        max_reconnect_delay = 30
        
        while self.running:
            try:
                events = get_gamepad()
                reconnect_delay = 1
                
                for event in events:
                    if not self.running:
                        break
                    self.input_handler.process_event(event, datetime.now())
                    
            except Exception as e:
                if self.running:
                    self.logger.error(f"Controller error: {e}")
                    self.input_handler.on_controller_disconnect()
                    time.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)
    
    def stop(self):
        """Stop reading controller inputs."""
        self.running = False
