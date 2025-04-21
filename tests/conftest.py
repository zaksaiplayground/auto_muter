"""Conftest utility for the tests."""

from unittest.mock import patch

import pytest

from auto_muter.audio_controller import AudioController
from auto_muter.audio_muter import AudioMuter


@pytest.fixture(name="mock_audio_controller")
def fixture_mock_audio_controller():
    """Fixture to patch the audio controller objects."""
    with (
        patch("auto_muter.audio_controller.AudioUtilities.GetSpeakers"),
        patch("auto_muter.audio_controller.IAudioEndpointVolume"),
        patch("auto_muter.audio_controller.ctypes"),
    ):
        yield AudioController()


@pytest.fixture
def audio_muter(mock_audio_controller):
    """Fixture to patch the audio controller config."""
    with (
        patch(
            "auto_muter.audio_muter.AudioController", return_value=mock_audio_controller
        ),
        patch(
            "auto_muter.audio_muter.get_audio_devices",
            return_value=[{"name": "Mic", "id": "1"}],
        ),
    ):
        yield AudioMuter()
