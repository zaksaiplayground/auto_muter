# tests/test_gui.py
import pytest
from unittest.mock import patch, MagicMock
from auto_muter.gui import AutoMuterGUI


@pytest.fixture
def mock_audio_muter():
    mock = MagicMock()
    mock.devices = [{"name": "Mic", "id": "1"}]
    mock.energy_threshold = 1000
    mock.silence_timeout = 1.0
    mock.initial_mute_state = True
    return mock


@pytest.fixture
def gui(mock_audio_muter):
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
def test_create_gui_does_not_run_mainloop(
    mock_doublevar,
    mock_intvar,
    mock_stringvar,
    mock_tk,
    mock_frame,
    mock_button,
    mock_combobox,
    mock_scale,
    mock_labelframe,
    mock_label,
    gui,
):
    root_mock = MagicMock()
    mock_tk.return_value = root_mock
    root_mock.mainloop = MagicMock()

    gui.create_gui()

    assert gui.root is not None
    root_mock.mainloop.assert_called_once()


def test_start_from_gui(gui):
    gui.device_var = MagicMock()
    gui.device_var.get.return_value = "Mic"

    gui.threshold_var = MagicMock()
    gui.threshold_var.get.return_value = 1500

    gui.timeout_var = MagicMock()
    gui.timeout_var.get.return_value = 2.0

    gui._start_from_gui()

    assert gui.audio_muter.input_device == "1"
    assert gui.audio_muter.energy_threshold == 1500
    assert gui.audio_muter.silence_timeout == 2.0
    gui.audio_muter.start.assert_called_once()


def test_stop_from_gui(gui):
    gui._stop_from_gui()
    gui.audio_muter.stop.assert_called_once()


def test_exit_application(gui):
    gui.root = MagicMock()
    gui._exit_application()
    gui.audio_muter.cleanup_before_exit.assert_called_once()
    gui.root.destroy.assert_called_once()
