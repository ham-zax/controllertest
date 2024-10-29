# Xbox Controller Input Counter

A Python application for monitoring Xbox controller inputs, recording macros, and modifying input signals.

## Features

- Real-time input monitoring
- Input counting with 1-second intervals
- Analog stick visualization
- Macro recording and playback
- Debug information display
- Input history logging

## Requirements

- Python 3.7+
- inputs library
- vgamepad library

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python src/main.py
```

## Project Structure

```
xbox_controller/
├── src/
│   ├── core/           # Core functionality
│   ├── gui/            # GUI components
│   ├── utils/          # Utility functions
│   ├── config/         # Configuration
│   └── main.py         # Entry point
├── tests/              # Test files
├── logs/               # Application logs
├── requirements.txt    # Dependencies
└── README.md          # Documentation
```

## License

MIT License
