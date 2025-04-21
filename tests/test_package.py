"""Unit test for the packaging module."""

from unittest.mock import MagicMock, mock_open, patch

from auto_muter.package import get_version, install, package_exe


@patch("auto_muter.package.logger")
@patch("auto_muter.package.PyInstaller.__main__.run", autospec=True)
def test_install_runs_pyinstaller(mock_run, mock_logger):
    """Test package installation."""
    install()
    mock_run.assert_called_once()
    mock_logger.info.assert_called_once_with("Build completed successfully!")


@patch("auto_muter.package.toml.load")
def test_get_version_returns_version(mock_toml):
    """test get_version from poetry."""
    mock_toml.return_value = {"project": {"version": "1.2.3"}}

    assert get_version() == "1.2.3"


@patch("auto_muter.package.install")
@patch("auto_muter.package.get_version", return_value="1.0.0")
@patch("auto_muter.package.Path.mkdir")
@patch("auto_muter.package.Path.exists", return_value=True)
@patch("auto_muter.package.zipfile.ZipFile")
@patch("auto_muter.package.setup_logger")
@patch("auto_muter.package.argparse.ArgumentParser")
def test_package_exe_creates_zip(  # pylint: disable=too-many-arguments
    mock_argparse,
    mock_logger,  # pylint: disable=unused-argument
    mock_zipfile,
    mock_exists,  # pylint: disable=unused-argument
    mock_mkdir,  # pylint: disable=unused-argument
    mock_get_version,  # pylint: disable=unused-argument
    mock_install,
):
    """Test creation of zip package."""
    mock_args = MagicMock()
    mock_args.path = "."
    mock_args.build = True
    mock_args.use_key = False

    mock_parser = MagicMock()
    mock_parser.parse_args.return_value = mock_args
    mock_argparse.return_value = mock_parser

    # Patch os.environ so GITHUB_OUTPUT doesn't exist
    with patch.dict("os.environ", {}, clear=True):

        package_exe()

    mock_install.assert_called_once()
    mock_zipfile.assert_called_once()


@patch("auto_muter.package.get_version", return_value="2.0.0")
@patch("auto_muter.package.Path.exists", return_value=True)
@patch("auto_muter.package.zipfile.ZipFile")
@patch("auto_muter.package.setup_logger")
@patch("auto_muter.package.argparse.ArgumentParser")
def test_package_exe_sets_github_output(
    mock_argparse,
    mock_logger,  # pylint: disable=unused-argument
    mock_zipfile,
    mock_exists,  # pylint: disable=unused-argument
    mock_version,  # pylint: disable=unused-argument
):
    """Test github output file writing."""
    mock_args = MagicMock()
    mock_args.path = "."
    mock_args.build = False
    mock_args.use_key = False

    mock_parser = MagicMock()
    mock_parser.parse_args.return_value = mock_args
    mock_argparse.return_value = mock_parser

    mock_zipfile_instance = MagicMock()
    mock_zipfile.return_value.__enter__.return_value = mock_zipfile_instance

    fake_output_file = "/fake/github_output.txt"
    with (
        patch.dict("os.environ", {"GITHUB_OUTPUT": fake_output_file}),
        patch("builtins.open", mock_open()) as m,
    ):

        package_exe()

        handle = m()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        assert "package_path=" in written
        assert "version=2.0.0" in written
