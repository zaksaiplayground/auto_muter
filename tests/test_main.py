from unittest.mock import patch
from auto_muter.main import main

def test_main_success():
    with patch("auto_muter.main.AudioMuter") as mock_muter_cls, \
         patch("auto_muter.main.AutoMuterGUI") as mock_gui_cls, \
         patch("auto_muter.main.setup_logger"):
        instance = mock_muter_cls.return_value
        gui_instance = mock_gui_cls.return_value

        result = main()

        mock_muter_cls.assert_called_once()
        mock_gui_cls.assert_called_once_with(instance)
        gui_instance.create_gui.assert_called_once()
        assert result == 0

def test_main_exception():
    with patch("auto_muter.main.AudioMuter", side_effect=Exception("fail")), \
         patch("auto_muter.main.setup_logger") as mock_logger:
        logger = mock_logger.return_value
        result = main()
        assert result == 1
        logger.error.assert_called()
