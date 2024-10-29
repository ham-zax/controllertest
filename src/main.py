"""Main entry point for the Xbox controller input counter application."""

import sys
from src.utils.logger import setup_logging
from src.gui.main_window import MainWindow

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import inputs
        import vgamepad
        return True
    except ImportError as e:
        print(f"\nMissing dependency: {e}")
        print("Please install required packages using: pip install -r requirements.txt")
        return False

def main():
    """Main application entry point."""
    try:
        # Setup logging
        logger = setup_logging()
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Create and run main window
        app = MainWindow()
        app.run()
        
    except Exception as e:
        print(f"\nError: {e}")
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
