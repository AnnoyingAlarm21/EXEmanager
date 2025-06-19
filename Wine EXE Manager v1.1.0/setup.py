#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from pathlib import Path

def install_requirements():
    """Install required packages"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_app():
    """Build the app using PyInstaller"""
    # Clean previous builds
    for path in ["build", "dist"]:
        if os.path.exists(path):
            shutil.rmtree(path)

    # Create app icon
    icon_path = create_icns()

    # Build the app
    subprocess.check_call([
        "pyinstaller",
        "--name=Wine EXE Manager",
        "--windowed",
        "--onefile",
        f"--icon={icon_path}",
        "--add-data=README.md:.",
        "--add-data=requirements.txt:.",
        "exe_manager.py"
    ])

def create_icns():
    """Create app icon"""
    try:
        from PIL import Image
        import io

        # Create a purple square icon with 'W' in the middle
        size = 512
        background_color = (142, 68, 173)  # Purple color
        icon = Image.new('RGB', (size, size), background_color)
        
        # Save as PNG
        icon_path = "app_icon.png"
        icon.save(icon_path)
        
        return icon_path
    except Exception as e:
        print(f"Warning: Could not create icon: {e}")
        return None

def create_zip():
    """Create ZIP file for distribution"""
    app_path = os.path.join("dist", "Wine EXE Manager.app")
    if os.path.exists(app_path):
        shutil.make_archive("Wine-EXE-Manager-macOS", "zip", "dist", "Wine EXE Manager.app")
        print(f"\nCreated Wine-EXE-Manager-macOS.zip")

def main():
    print("Setting up Wine EXE Manager...")
    
    # Ensure we have all requirements
    print("\nInstalling requirements...")
    install_requirements()
    
    # Build the app
    print("\nBuilding app...")
    build_app()
    
    # Create distribution ZIP
    print("\nCreating distribution package...")
    create_zip()
    
    print("\nDone! You can find the app in the dist directory and the ZIP package in the current directory.")

if __name__ == "__main__":
    main() 