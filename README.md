# Auto Muter

Automatically mutes and unmutes your microphone based on voice detection.

## Features

- Voice activity detection to automatically unmute when you start speaking
- Automatically mutes after a configurable period of silence
- Hotkey support for manual muting/unmuting
- User-friendly GUI for configuration
- Windows audio API integration for reliable mute control

## Requirements

- Windows operating system
- Required Python packages (installed with poetry):
  - numpy
  - PyAudio
  - keyboard
  - pycaw

## Installation

```bash
poetry install
```

## Usage

### Running the application

After installation, you can run the app using:

```bash
python .\auto_muter\main.py
```

### Configuration

The GUI allows you to configure:

1. Input device selection
2. Voice detection sensitivity (Energy threshold)
3. Silence timeout before auto-muting
4. Custom hotkey for manual mute toggling

## Troubleshooting

Check the log file in the `C:\Users\<user_name>\AppData\Local\AutoMuter\logs` directory for detailed information if you encounter any issues.

Common issues:

- **No audio devices detected**: Ensure your microphone is properly connected and enabled in Windows
- **Application not muting**: Try increasing the energy threshold for voice detection

## Acknowledgments

- Thanks to the PyAudio team for the audio processing library
- Thanks to the pycaw team for Windows Core Audio API integration
