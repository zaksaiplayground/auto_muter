import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_audio_controller():
    controller = MagicMock()
    controller.toggle_mute.return_value = False  # Simulate unmuted
    return controller

@pytest.fixture
def patched_audio_muter(mock_audio_controller):
    with patch("auto_muter.audio_muter.AudioController", return_value=mock_audio_controller), \
         patch("auto_muter.audio_muter.get_audio_devices", return_value=[{"name": "Default", "id": "default"}]):
        from auto_muter.audio_muter import AudioMuter
        yield AudioMuter()
