#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to that directory
cd "$DIR"

# Check if Python 3 is installed
if command -v python3 &>/dev/null; then
    # Check if requirements are installed
    if ! python3 -c "import requests, tqdm" &>/dev/null; then
        echo "Installing required packages..."
        pip3 install -r requirements.txt
    fi
    
    # Run the wrapper script instead of exe_manager.py directly
    python3 run_app.py
else
    echo "Python 3 is required but not installed."
    echo "Please install Python 3 from https://www.python.org/downloads/"
    read -p "Press Enter to exit..."
fi 