"""Unit test for the gui module."""

from unittest.mock import MagicMock, patch

import pytest

from auto_muter.gui import AutoMuterGUI


@pytest.fixture(name="mock_audio_muter")
def fixture_mock_audio_muter():
    """Fixture for mocking audio muter."""
    mock = MagicMock()
    mock.devices = [{"name": "Mic", "id": "1"}]
    mock.energy_threshold = 1000
    mock.silence_timeout = 1.0
    mock.initial_mute_state = True
    return mock


@pytest.fixture(name="mock_gui")
def fixture_mock_gui(mock_audio_muter):
    """Fixture for mocking GUI."""
    return AutoMuterGUI(mock_audio_muter)


@patch("auto_muter.gui.ttk.Label")
@patch("auto_muter.gui.ttk.LabelFrame")
@patch("auto_muter.gui.ttk.Scale")
@patch("auto_muter.gui.ttk.Combobox")
@patch("auto_muter.gui.ttk.Button")
@patch("auto_muter.gui.ttk.Frame")
@patch("auto_muter.gui.tk.Tk")
@patch("auto_muter.gui.tk.StringVar")
@patch("auto_muter.gui.tk.IntVar")
@patch("auto_muter.gui.tk.DoubleVar")
def test_create_gui_does_not_run_mainloop(  # pylint: disable=too-many-arguments
    mock_doublevar,  # pylint: disable=unused-argument
    mock_intvar,  # pylint: disable=unused-argument
    mock_stringvar,  # pylint: disable=unused-argument
    mock_tk,  # pylint: disable=unused-argument
    mock_frame,  # pylint: disable=unused-argument
    mock_button,  # pylint: disable=unused-argument
    mock_combobox,  # pylint: disable=unused-argument
    mock_scale,  # pylint: disable=unused-argument
    mock_labelframe,  # pylint: disable=unused-argument
    mock_label,  # pylint: disable=unused-argument
    mock_gui,  # pylint: disable=unused-argument
):
    """Test gui creation."""
    root_mock = MagicMock()
    mock_tk.return_value = root_mock
    root_mock.mainloop = MagicMock()

    mock_gui.create_gui()

    assert mock_gui.root is not None
    root_mock.mainloop.assert_called_once()


def test_start_from_gui(mock_gui):
    """Test the start button functionality."""
    mock_gui.device_var = MagicMock()
    mock_gui.device_var.get.return_value = "Mic"

    mock_gui.threshold_var = MagicMock()
    mock_gui.threshold_var.get.return_value = 1500

    mock_gui.timeout_var = MagicMock()
    mock_gui.timeout_var.get.return_value = 2.0

    mock_gui._start_from_gui()  # pylint: disable=protected-access

    assert mock_gui.audio_muter.input_device == "1"
    assert mock_gui.audio_muter.energy_threshold == 1500
    assert mock_gui.audio_muter.silence_timeout == 2.0
    mock_gui.audio_muter.start.assert_called_once()


def test_stop_from_gui(mock_gui):
    """Test the stop button functionality."""
    mock_gui._stop_from_gui()  # pylint: disable=protected-access
    mock_gui.audio_muter.stop.assert_called_once()


def test_exit_application(mock_gui):
    """Test the exit button functionality."""
    mock_gui.root = MagicMock()
    mock_gui._exit_application()  # pylint: disable=protected-access
    mock_gui.audio_muter.cleanup_before_exit.assert_called_once()
    mock_gui.root.destroy.assert_called_once()
