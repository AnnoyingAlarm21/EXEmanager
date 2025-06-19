#!/bin/bash

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    osascript -e 'display dialog "Python 3 is required but not installed. Please install Python 3 from python.org" buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Launch the application
python3 exe_manager.py 