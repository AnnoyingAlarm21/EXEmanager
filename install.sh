#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to that directory
cd "$DIR"

# Check if Python 3 is installed
if ! command -v python3 &>/dev/null; then
    echo "Python 3 is required but not installed."
    echo "Please install Python 3 from https://www.python.org/downloads/"
    read -p "Press Enter to exit..."
    exit 1
fi

# Install required packages
echo "Installing required packages..."
pip3 install -r requirements.txt

# Generate icon
echo "Generating application icon..."
python3 icon_generator.py

# Create app bundle
echo "Creating application bundle..."
python3 package_app.py

# Ask if user wants to move the app to Applications
read -p "Do you want to move Wine EXE Manager to the Applications folder? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Moving to Applications folder..."
    cp -R "Wine EXE Manager.app" "/Applications/"
    echo "Wine EXE Manager has been installed to the Applications folder."
else
    echo "Wine EXE Manager app bundle has been created in the current directory."
fi

echo "Installation complete!" 