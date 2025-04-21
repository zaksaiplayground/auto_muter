"""Unit test for the Audio controller module."""

from unittest.mock import MagicMock


def test_audio_controller_initialization(mock_audio_controller):
    """Test audio controller initialization."""
    controller = mock_audio_controller
    assert controller.initialized is True


def test_get_mute_state(mock_audio_controller):
    """Test get current mute state."""
    mock_audio_controller.volume.GetMute = MagicMock(return_value=1)
    assert mock_audio_controller.get_mute_state() is True


def test_set_mute_state_mute(mock_audio_controller):
    """Test the setting of mute state as mute."""
    mock_audio_controller.volume.SetMute = MagicMock()
    result = mock_audio_controller.set_mute_state(True)
    assert result is True


def test_toggle_mute(mock_audio_controller):
    """Test the toggling of mute state."""
    mock_audio_controller.volume.GetMute = MagicMock(return_value=False)
    mock_audio_controller.volume.SetMute = MagicMock()
    result = mock_audio_controller.toggle_mute()
    assert result is True
