"""Application settings and configuration."""

class Settings:
    def __init__(self):
        # Window settings
        self.window_title = "Xbox Controller Input Counter & Macro Recorder"
        self.window_size = "1200x800"
        
        # Input thresholds
        self.analog_max = 32767
        self.analog_threshold = 3000
        self.analog_deadzone = 0.1
        self.trigger_threshold = 100
        
        # Font settings
        self.font_family = 'Arial'
        self.font_size_normal = 12
        self.font_size_small = 10
        
        # File paths
        self.macro_file = 'macros.json'
        self.state_file = 'app_state.json'
        self.log_file = 'logs/controller_counter.log'
        
        # Macro settings
        self.default_macro_speed = 1.0
        self.max_macro_name_length = 50
        
        # History settings
        self.max_history_entries = 1000
        self.history_timestamp_format = "%H:%M:%S.%f"
