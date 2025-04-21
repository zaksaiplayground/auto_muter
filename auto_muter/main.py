"""Startup script for AutoMuter"""

# TODO: add poetry/pip dependency security checks
# TODO: find vulnerability in code - https://github.com/PyCQA/bandit, sonarqube
import sys

from auto_muter.audio_muter import AudioMuter
from auto_muter.gui import AutoMuterGUI
from auto_muter.logger import setup_logger


def main():
    """Main entrypoint for the application."""
    # Setup logging
    logger = setup_logger()
    logger.info("Starting Auto Muter")

    try:
        # Create audio muter instance
        audio_muter = AudioMuter()

        # Create and start GUI
        gui = AutoMuterGUI(audio_muter)
        gui.create_gui()

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Error in main application: %s", e)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
