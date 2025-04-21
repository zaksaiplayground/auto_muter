# conftest.py
import pytest
from unittest.mock import patch
from auto_muter.audio_controller import AudioController
from auto_muter.audio_muter import AudioMuter

@pytest.fixture
def mock_audio_controller():
    with patch("auto_muter.audio_controller.AudioUtilities.GetSpeakers"), \
         patch("auto_muter.audio_controller.IAudioEndpointVolume"), \
         patch("auto_muter.audio_controller.ctypes"):
        yield AudioController()

@pytest.fixture
def audio_muter(mock_audio_controller):
    with patch("auto_muter.audio_muter.AudioController", return_value=mock_audio_controller), \
         patch("auto_muter.audio_muter.get_audio_devices", return_value=[{"name": "Mic", "id": "1"}]):
        yield AudioMuter()
