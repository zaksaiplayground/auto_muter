"""Utility module for application."""

import logging

import pyaudio

logger = logging.getLogger(__name__)


def get_audio_devices():
    """Get audio input devices for Windows"""
    devices = []

    try:
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info["maxInputChannels"] > 0:  # It's an input device
                name = device_info["name"]
                devices.append({"name": name, "id": str(i)})
        p.terminate()
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Error getting devices with PyAudio: %s", e)

    # Always add default device
    if not any(d["id"] == "default" for d in devices):
        devices.insert(0, {"name": "Default Microphone", "id": "default"})

    return devices
