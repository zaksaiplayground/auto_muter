#!/bin/bash

# Update package listings
sudo apt-get update

# Install required system packages
sudo apt-get install -y portaudio19-dev python3-pyaudio pulseaudio alsa-utils libsndfile1 sox

# Install required audio tools for the pure Python approach
sudo apt-get install -y alsa-utils sox ffmpeg

# # Create a new conda environment without using the system libraries
# conda create -n audio_muter python=3.10 -y

# Activate the environment
eval "$(conda shell.bash hook)"
conda activate audio_muter

# Install basic dependencies that don't have complex C dependencies
conda install -c conda-forge numpy -y
pip install PySimpleGUI keyboard pynput

# Install Poetry if not installed
if ! command -v poetry &> /dev/null; then
    curl -sSL https://install.python-poetry.org | python3 -
    # Add Poetry to PATH
    export PATH="$HOME/.local/bin:$PATH"
fi

# # Create project structure
# mkdir -p auto_muter
# cd auto_muter

# # Initialize Poetry project
# poetry init -n

# Add dependencies using poetry
poetry add numpy PySimpleGUI keyboard pynput

echo "Setup complete! Use 'conda activate audio_muter' to activate the environment."