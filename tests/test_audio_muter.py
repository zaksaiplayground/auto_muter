import time

def test_initial_state(patched_audio_muter):
    assert patched_audio_muter.running is False
    assert patched_audio_muter.muted is True
    assert isinstance(patched_audio_muter.devices, list)

def test_toggle_mute_sets_state(patched_audio_muter):
    patched_audio_muter.muted = True
    patched_audio_muter.toggle_mute()
    assert patched_audio_muter.muted is False

def test_start_sets_running_and_thread(patched_audio_muter):
    patched_audio_muter.start()
    assert patched_audio_muter.running is True
    time.sleep(0.1)  # allow thread to initialize
    patched_audio_muter.stop()
    assert patched_audio_muter.running is False

def test_stop_gracefully_stops_thread(patched_audio_muter):
    patched_audio_muter.start()
    patched_audio_muter.stop()
    assert patched_audio_muter.running is False
    if patched_audio_muter.audio_thread:
        assert not patched_audio_muter.audio_thread.is_alive()
