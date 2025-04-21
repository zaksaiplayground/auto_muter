"""Utility script to build and package application."""

# TODO: add tests
import argparse
import os
import zipfile
from pathlib import Path

import PyInstaller.__main__
import toml

from auto_muter.logger import setup_logger

HERE = Path(__file__).parent.parent.absolute()
path_to_main = str(HERE / "auto_muter" / "main.py")

logger = setup_logger()


def install():
    cmd = [
        path_to_main,
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--noupx",
        "--name=AutoMuter",
        "--distpath=dist",
        "--workpath=build",
        "--specpath=build",
    ]

    PyInstaller.__main__.run(cmd)
    logger.info("Build completed successfully!")


def get_version():
    pyproject = toml.load(HERE / "pyproject.toml")
    return pyproject["project"]["version"]


def package_exe():
    parser = argparse.ArgumentParser(description="Package AutoMuter executable.")
    parser.add_argument(
        "--path",
        type=str,
        default=".",  # Default to current working directory
        help="The path to store the packaged .zip (default is current directory)",
    )
    parser.add_argument(
        "--use-key", action="store_true", help="Use encryption key with PyInstaller"
    )
    parser.add_argument("--build", action="store_true", help="Build before packaging")
    args = parser.parse_args()

    if args.build:
        install()

    output_dir = Path(args.path)
    output_dir.mkdir(parents=True, exist_ok=True)

    dist_dir = Path("dist")
    exe_path = dist_dir / "AutoMuter.exe"
    version = get_version()
    zip_filename = f"AutoMuter-v{version}.zip"
    zip_path = output_dir / zip_filename

    if exe_path.exists():
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(exe_path, arcname="AutoMuter.exe")
        logger.info(f"Packaged: {zip_path}")

        output_file = os.environ.get("GITHUB_OUTPUT")
        if output_file:
            with open(output_file, "a") as f:
                f.write(f"package_path={zip_path}\n")
                f.write(f"version={version}\n")
        else:
            logger.warning("GITHUB_OUTPUT not set, skipping output write.")


def build_and_package():
    install()
    package_exe()
