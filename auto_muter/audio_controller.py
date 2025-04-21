"""Audio Controller using Windows Core Audio API."""

import ctypes
import logging
import math
import time

import comtypes
import numpy as np
from comtypes import CLSCTX_ALL
from pycaw.pycaw import (DEVICE_STATE, AudioUtilities, EDataFlow,
                         IAudioEndpointVolume, IAudioMeterInformation,
                         IMMDeviceEnumerator)

logger = logging.getLogger(__name__)


class AudioController:
    """Controls audio functions using Windows Core Audio API"""

    def __init__(self):
        """Initialize the audio controller"""
        self.initialized = False
        self.output_monitor_initialized = False

        try:
            # Get default audio device
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None
            )  # noqa: E501
            self.volume = ctypes.cast(
                interface, ctypes.POINTER(IAudioEndpointVolume)
            )  # noqa: E501

            # Initialize audio level meter for output detection
            meter_interface = devices.Activate(
                IAudioMeterInformation._iid_, CLSCTX_ALL, None
            )
            self.audio_meter = ctypes.cast(
                meter_interface, ctypes.POINTER(IAudioMeterInformation)
            )

            self.initialized = True
            self.output_monitor_initialized = True
            logger.info("Audio controller initialized successfully")

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to initialize audio controller: %s", e)

    def is_audio_playing(self):
        """
        Check if any audio is currently playing through the speakers

        Returns:
            bool: True if audio is playing, False otherwise
        """
        if not self.output_monitor_initialized:
            return False

        try:
            # Get the peak value from the audio meter
            peak_value = self.audio_meter.GetPeakValue()

            # Check if the peak is above the threshold (adjust as needed)
            # Using -60dB as threshold (very quiet sound)
            threshold = 0.001  # Approximately -60dB

            is_playing = peak_value > threshold

            if is_playing:
                peak_db = 20 * math.log10(peak_value) if peak_value > 0 else -100
                logger.debug(f"Audio detected: Peak level = {peak_db:.1f}dB")

            return is_playing

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error checking if audio is playing: %s", e)
            return False

    def get_peak_meter_value(self):
        """
        Get the current peak meter value for output audio

        Returns:
            float: Peak audio level (0.0 to 1.0) or -1 if error
        """
        if not self.output_monitor_initialized:
            return -1

        try:
            return self.audio_meter.GetPeakValue()
        except Exception as e:
            logger.error("Error getting peak meter value: %s", e)
            return -1

    def get_mute_state(self):
        """
        Get the current mute state of the system

        Returns:
            bool or None: Current mute state (True=muted, False=unmuted),
                          or None if state couldn't be determined
        """
        if self.initialized:
            try:
                return bool(self.volume.GetMute())
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Error setting mute state: %s", e)
        return None  # Return None if we can't determine the state

    def set_mute_state(self, should_mute):
        """
        Set the mute state to a specific value

        Args:
            should_mute (bool): True to mute, False to unmute

        Returns:
            bool or None: New mute state, or None if state couldn't be determined
        """
        if self.initialized:
            try:
                self.volume.SetMute(bool(should_mute), None)
                return should_mute  # Return new mute state
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Error setting mute state: %s", e)

        # Backup method: use media keys (can only toggle, not set specific state)
        try:
            # Get current state first
            current_state = self.get_mute_state()

            # Only press mute key if needed
            if current_state is not None and current_state != should_mute:
                # VK_VOLUME_MUTE = 0xAD
                ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
                return should_mute
            if current_state is not None:
                # Already in desired state
                return current_state

            # Can't determine actual state
            return None
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error setting mute with media keys: %s", e)
            return None

    def toggle_mute(self):
        """
        Toggle mute state using audio controller

        Returns:
            bool or None: New mute state, or None if state couldn't
                          be determined
        """
        if self.initialized:
            try:
                current_mute = self.volume.GetMute()
                self.volume.SetMute(not current_mute, None)
                return not current_mute  # Return new mute state
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Error toggling mute with audio controller: %s", e)

        # Backup method: use media keys
        try:
            # VK_VOLUME_MUTE = 0xAD
            ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
            # Can't determine actual state, so return None
            return None
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error toggling mute with media keys: %s", e)
            return None
