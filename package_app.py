#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_app_bundle():
    """Create a macOS app bundle for the Wine EXE Manager"""
    # Get the directory where this script is located
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create app bundle structure
    bundle_name = "Wine EXE Manager.app"
    bundle_path = os.path.join(app_dir, bundle_name)
    contents_path = os.path.join(bundle_path, "Contents")
    macos_path = os.path.join(contents_path, "MacOS")
    resources_path = os.path.join(contents_path, "Resources")
    
    # Remove existing bundle if it exists
    if os.path.exists(bundle_path):
        shutil.rmtree(bundle_path)
    
    # Create directories
    os.makedirs(macos_path, exist_ok=True)
    os.makedirs(resources_path, exist_ok=True)
    
    # Create Info.plist
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>run.sh</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.wineexemanager.app</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Wine EXE Manager</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
"""
    
    with open(os.path.join(contents_path, "Info.plist"), "w") as f:
        f.write(info_plist)
    
    # Create run script
    run_script = """#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESOURCES_DIR="$DIR/../Resources"

# Change to the resources directory
cd "$RESOURCES_DIR"

# Check if Python 3 is installed
if command -v python3 &>/dev/null; then
    # Check if requirements are installed
    if ! python3 -c "import requests, tqdm, PIL, PyQt5" &>/dev/null; then
        echo "Installing required packages..."
        pip3 install -r requirements.txt
    fi
    
    # Run the application via the wrapper script
    python3 run_app.py
else
    osascript -e 'display dialog "Python 3 is required but not installed. Please install Python 3 from https://www.python.org/downloads/" buttons {"OK"} default button "OK" with icon stop'
fi
"""
    
    with open(os.path.join(macos_path, "run.sh"), "w") as f:
        f.write(run_script)
    
    # Make the run script executable
    os.chmod(os.path.join(macos_path, "run.sh"), 0o755)
    
    # Copy application files to Resources
    files_to_copy = [
        "exe_manager.py",
        "wine_installer.py",
        "requirements.txt",
        "README.md",
        "run_app.py"
    ]
    
    for file in files_to_copy:
        file_path = os.path.join(app_dir, file)
        if os.path.exists(file_path):
            shutil.copy2(file_path, resources_path)
    
    # Generate icon if not exists
    icon_path = os.path.join(app_dir, "app_icon.png")
    if not os.path.exists(icon_path):
        try:
            # Try to import the icon generator and generate an icon
            from icon_generator import generate_icon
            icon_path = generate_icon()
        except ImportError:
            print("Could not generate icon. Using default.")
    
    # Convert PNG to ICNS if icon exists
    if os.path.exists(icon_path):
        try:
            # Create iconset directory
            iconset_path = os.path.join(app_dir, "AppIcon.iconset")
            if os.path.exists(iconset_path):
                shutil.rmtree(iconset_path)
            os.makedirs(iconset_path, exist_ok=True)
            
            # Generate different icon sizes
            icon_sizes = [16, 32, 64, 128, 256, 512]
            for size in icon_sizes:
                subprocess.run([
                    "sips",
                    "-z", str(size), str(size),
                    icon_path,
                    "--out", os.path.join(iconset_path, f"icon_{size}x{size}.png")
                ])
                # Also create 2x versions
                if size * 2 <= 512:  # Don't exceed the original size
                    subprocess.run([
                        "sips",
                        "-z", str(size*2), str(size*2),
                        icon_path,
                        "--out", os.path.join(iconset_path, f"icon_{size}x{size}@2x.png")
                    ])
            
            # Convert iconset to icns
            icns_path = os.path.join(resources_path, "AppIcon.icns")
            subprocess.run([
                "iconutil",
                "-c", "icns",
                iconset_path,
                "-o", icns_path
            ])
            
            # Clean up
            shutil.rmtree(iconset_path)
            
        except Exception as e:
            print(f"Error creating icon: {e}")
    
    print(f"App bundle created at: {bundle_path}")
    return bundle_path

if __name__ == "__main__":
    create_app_bundle() 