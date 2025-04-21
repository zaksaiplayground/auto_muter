"""Startup script for AutoMuter"""

# TODO: add tests
# FIXME: the git version tag should reflect the pyproject.toml versions
# TODO: add poetry/pip dependency security checks
# TODO: find vulnerability in code - https://github.com/PyCQA/bandit, sonarqube
# TODO: find a secure way to ensure no issues with exe and Windows defender
# https://stackoverflow.com/questions/252226/signing-a-windows-exe-file
import sys

from auto_muter.audio_muter import AudioMuter
from auto_muter.gui import AutoMuterGUI
from auto_muter.logger import setup_logger


def main():
    # Setup logging
    logger = setup_logger()
    logger.info("Starting Auto Muter")

    try:
        # Create audio muter instance
        audio_muter = AudioMuter()

        # Create and start GUI
        gui = AutoMuterGUI(audio_muter)
        gui.create_gui()

    except Exception as e:
        logger.error(f"Error in main application: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
