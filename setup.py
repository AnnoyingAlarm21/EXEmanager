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

def create_icns():
    """Create app icon"""
    if not os.path.exists("app_icon.png"):
        print("Warning: app_icon.png not found, using default icon")
        return None
        
    icons_dir = "app.iconset"
    if os.path.exists(icons_dir):
        shutil.rmtree(icons_dir)
    os.makedirs(icons_dir)
    
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    for size in sizes:
        subprocess.call([
            "sips",
            "-z", str(size), str(size),
            "app_icon.png",
            "--out", f"{icons_dir}/icon_{size}x{size}.png"
        ])
        if size <= 512:  # Create @2x versions for retina
            subprocess.call([
                "sips",
                "-z", str(size*2), str(size*2),
                "app_icon.png",
                "--out", f"{icons_dir}/icon_{size}x{size}@2x.png"
            ])
    
    subprocess.call(["iconutil", "-c", "icns", icons_dir])
    shutil.rmtree(icons_dir)
    return "app.icns"

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
        "--onedir",
        f"--icon={icon_path}" if icon_path else "",
        "--add-data=README.md:.",
        "--add-data=requirements.txt:.",
        "--add-data=wine_installer.py:.",
        "--add-data=app_icon.png:.",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "exe_manager.py"
    ])
    
    # Clean up icon
    if icon_path and os.path.exists(icon_path):
        os.remove(icon_path)
    
    # Create ZIP archive
    app_path = "dist/Wine EXE Manager.app"
    if os.path.exists(app_path):
        shutil.make_archive("Wine-EXE-Manager-v1.1.0-macOS", "zip", "dist", "Wine EXE Manager.app")
        print(f"\nApp bundle created successfully at: {app_path}")
        print("ZIP archive created: Wine-EXE-Manager-v1.1.0-macOS.zip")
    else:
        print("Error: App bundle creation failed")

if __name__ == "__main__":
    print("Installing requirements...")
    install_requirements()
    
    print("\nBuilding app bundle...")
    build_app() 