"""Unit test for the audio muter module."""


def test_initial_state(audio_muter):
    """Test the initial state."""
    assert audio_muter.muted is True
    assert audio_muter.running is False


def test_toggle_mute(audio_muter):
    """Test the toggle mute functionality."""
    audio_muter.audio_controller.toggle_mute = lambda: False
    audio_muter.toggle_mute()
    assert audio_muter.muted is False


def test_set_mute_state(audio_muter):
    """Test the mute setting functionality."""
    audio_muter.set_mute_state(True)
    assert audio_muter.muted is True
    audio_muter.set_mute_state(False)
    assert audio_muter.muted is False


def test_start_and_stop(audio_muter):
    """Test the start and stop of muting functionality."""
    audio_muter.audio_controller.set_mute_state = lambda x: x
    audio_muter.start()
    assert audio_muter.running is True
    audio_muter.stop()
    assert audio_muter.running is False
