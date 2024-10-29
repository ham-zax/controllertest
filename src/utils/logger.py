"""Logging configuration and setup."""

import os
import logging

def setup_logging():
    """Configure logging for the application."""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/controller_counter.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('ControllerCounter')
