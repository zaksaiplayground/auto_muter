import ctypes
import logging

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

logger = logging.getLogger(__name__)


class AudioController:
    """Controls audio functions using Windows Core Audio API"""

    def __init__(self):
        """Initialize the audio controller"""
        self.initialized = False
        try:
            # Get default audio device
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
            self.initialized = True
            logger.info("Audio controller initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize audio controller: {e}", exc_info=True)
            # Fallback to media key method
            pass

    def toggle_mute(self):
        """
        Toggle mute state using audio controller

        Returns:
            bool or None: New mute state, or None if state couldn't be determined
        """
        if self.initialized:
            try:
                current_mute = self.volume.GetMute()
                self.volume.SetMute(not current_mute, None)
                return not current_mute  # Return new mute state
            except Exception as e:
                logger.error(
                    f"Error toggling mute with audio controller: {e}", exc_info=True
                )

        # Backup method: use media keys
        try:
            # VK_VOLUME_MUTE = 0xAD
            ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
            # Can't determine actual state, so return None
            return None
        except Exception as e:
            logger.error(f"Error toggling mute with media keys: {e}", exc_info=True)
            return None
