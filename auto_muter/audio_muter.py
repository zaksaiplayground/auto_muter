"""Core auto-muting functionality handler."""

import logging
import struct
import threading
import time

import numpy as np
import pyaudio

from auto_muter.audio_controller import AudioController
from auto_muter.utils import get_audio_devices

logger = logging.getLogger(__name__)


class AudioMuter:
    """Core auto-muting functionality with voice detection"""

    def __init__(self):
        """Initialize the AudioMuter"""
        self.running = False
        self.muted = True
        # Track the initial mute state for restoring when stopped
        # self.initial_mute_state = None
        self.energy_threshold = 1000  # Adjust for sensitivity
        self.silence_timeout = 1.0  # Seconds of silence before muting
        self.last_sound_time = time.time()

        # Initialize audio controller
        self.audio_controller = AudioController()

        # Get list of input devices for Windows
        try:
            self.devices = get_audio_devices()
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error getting audio devices: %s", e)
            self.devices = [{"name": "Default", "id": "default"}]

        self.input_device = "default"
        self.chunk_size = 1024
        self.audio_thread = None

        # Get the initial mute state when the application starts
        self._capture_initial_mute_state()

    def _capture_initial_mute_state(self):
        """Capture the initial mute state of the system"""
        try:
            if self.audio_controller.initialized:
                self.initial_mute_state = self.audio_controller.get_mute_state()
                logger.error(
                    "Initial mute state captured: %s",
                    "Muted" if self.initial_mute_state else "Unmuted",
                )
            else:
                logger.warning(
                    "Could not capture initial mute state: audio controller not initialized"
                )
                self.initial_mute_state = (
                    False  # Default assumption if we can't determine
                )
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error capturing initial mute state: %s", e)
            self.initial_mute_state = False  # Default assumption if we can't determine

    def _record_and_process_audio(self):
        """Record audio and process it for voice detection"""
        try:
            self._record_with_pyaudio()
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error in audio processing: %s", e)
            self.running = False
            self._update_gui_status(f"Error: {str(e)}")

    def _record_with_pyaudio(self):
        """Record and process audio using PyAudio"""

        chunk = self.chunk_size
        format = pyaudio.paInt16
        channels = 1
        rate = 16000

        try:
            p = pyaudio.PyAudio()

            # Get the device index if not using default
            device_index = None
            if self.input_device != "default" and self.input_device.isdigit():
                device_index = int(self.input_device)

            # Open the stream
            stream = p.open(
                format=format,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=chunk,
                input_device_index=device_index,
            )

            logger.error("Started PyAudio stream on device: %s", self.input_device)

            while self.running:
                try:
                    # Read audio data
                    data = stream.read(chunk, exception_on_overflow=False)

                    # Calculate energy
                    fmt = f"{len(data)//2}h"
                    pcm_data = struct.unpack(fmt, data)
                    energy = np.sqrt(np.mean(np.array(pcm_data) ** 2))

                    # If speaking is detected
                    if energy > self.energy_threshold:
                        self.last_sound_time = time.time()
                        if self.muted:
                            self.toggle_mute()
                    # If silence for longer than timeout
                    elif (
                        not self.muted
                        and time.time() - self.last_sound_time > self.silence_timeout
                    ):
                        self.toggle_mute()

                except IOError as e:
                    # Handle overflow errors
                    logger.error("PyAudio read error (overflow): %s", e)

                # Small sleep to prevent CPU hogging
                time.sleep(0.01)

            # Clean up
            stream.stop_stream()
            stream.close()
            p.terminate()
            logger.info("PyAudio stream closed")

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error in PyAudio processing: %s", e)
            self.running = False
            self._update_gui_status(f"Error: {str(e)}")

    def _update_gui_status(self, message):
        """Update GUI status if available"""
        if hasattr(self, "run_status_label") and self.run_status_label:
            self.run_status_label.config(text=f"Status: {message}")

    def toggle_mute(self):
        """Toggle mute status using audio controller"""
        if self.running or True:  # Allow manual testing even when not running
            # Use our audio controller
            new_state = self.audio_controller.toggle_mute()

            # If we got a specific state back, use it
            if new_state is not None:
                self.muted = new_state
            else:
                # Otherwise just toggle our internal state
                self.muted = not self.muted

            # Print status update
            status = "Muted" if self.muted else "Unmuted"
            logger.error("Auto: %s", status)

            # Update GUI if it exists
            if hasattr(self, "status_label") and self.status_label:
                mute_text = "Muted" if self.muted else "Unmuted"
                self.status_label.config(text=f"Current State: {mute_text}")

    def set_mute_state(self, should_mute):
        """
        Set the mute state to a specific value

        Args:
            should_mute (bool): True to mute, False to unmute
        """
        new_state = self.audio_controller.set_mute_state(should_mute)

        if new_state is not None:
            self.muted = new_state
        else:
            self.muted = should_mute

        status = "Muted" if self.muted else "Unmuted"
        logger.error("Manually set: %s", status)

        # Update GUI if it exists
        if hasattr(self, "status_label") and self.status_label:
            mute_text = "Muted" if self.muted else "Unmuted"
            self.status_label.config(text=f"Current State: {mute_text}")

    def start(self):
        """Start monitoring and auto-muting"""
        if self.running:
            return

        # Always mute on startup regardless of current state
        self.set_mute_state(True)  # Force mute
        self.running = True
        self.last_sound_time = time.time()

        # Start audio monitoring in a separate thread
        self.audio_thread = threading.Thread(target=self._record_and_process_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()

        # Update GUI if it exists
        if hasattr(self, "run_status_label") and self.run_status_label:
            self.run_status_label.config(text="Status: Running")

        logger.info("Auto-Muter started!")

    def stop(self):
        """Stop monitoring and restore initial mute state"""
        if not self.running:
            return

        self.running = False
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)

        # Restore to initial mute state when stopping
        if self.initial_mute_state is not None:
            logger.error(
                "Restoring to initial mute state: %s",
                "Muted" if self.initial_mute_state else "Unmuted",
            )
            self.set_mute_state(self.initial_mute_state)

        # Update GUI if it exists
        if hasattr(self, "run_status_label") and self.run_status_label:
            self.run_status_label.config(text="Status: Stopped")

        logger.info("Auto-Muter stopped!")

    def cleanup_before_exit(self):
        """Restore initial mute state before exiting the application"""
        # Stop monitoring if still running
        if self.running:
            self.stop()
        elif self.initial_mute_state is not None:
            # If already stopped but need to restore mute state
            logger.error(
                "Restoring to initial mute state before exit: %s",
                "Muted" if self.initial_mute_state else "Unmuted",
            )
            self.set_mute_state(self.initial_mute_state)
