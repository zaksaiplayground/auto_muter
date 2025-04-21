# tests/test_utils.py
import pytest
from unittest.mock import patch, MagicMock
from auto_muter.utils import get_audio_devices


@patch("auto_muter.utils.pyaudio.PyAudio")
def test_get_audio_devices_with_inputs(mock_pyaudio):
    mock_instance = MagicMock()
    mock_pyaudio.return_value = mock_instance

    mock_instance.get_device_count.return_value = 2
    mock_instance.get_device_info_by_index.side_effect = [
        {"name": "Mic 1", "maxInputChannels": 2},
        {"name": "Speaker", "maxInputChannels": 0},
    ]

    devices = get_audio_devices()

    assert {"name": "Mic 1", "id": "0"} in devices
    assert any(d["id"] == "default" for d in devices)
    assert len(devices) == 2


@patch("auto_muter.utils.pyaudio.PyAudio", side_effect=Exception("pyaudio boom"))
def test_get_audio_devices_error(mock_pyaudio):
    devices = get_audio_devices()

    # Should still include default even if PyAudio fails
    assert len(devices) == 1
    assert devices[0]["id"] == "default"
