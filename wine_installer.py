#!/usr/bin/env python3
import os
import sys
import subprocess
import requests
import shutil
import tempfile
import zipfile
import tarfile
from tqdm import tqdm

def download_file(url, destination):
    """Download a file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    
    with open(destination, 'wb') as file, tqdm(
            desc=os.path.basename(destination),
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
        for data in response.iter_content(block_size):
            size = file.write(data)
            bar.update(size)

def install_wine():
    """Download and install a portable version of Wine"""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    wine_dir = os.path.join(app_dir, "wine")
    
    # Create wine directory if it doesn't exist
    if os.path.exists(wine_dir):
        shutil.rmtree(wine_dir)
    os.makedirs(wine_dir, exist_ok=True)
    
    # Create a temporary directory for downloads
    with tempfile.TemporaryDirectory() as temp_dir:
        # Try to download a simple Wine script that can be used without installation
        print("Creating portable Wine script...")
        
        # Create a simple wine script that will use the system wine if available
        wine_script_path = os.path.join(wine_dir, "bin")
        os.makedirs(wine_script_path, exist_ok=True)
        
        wine_script = os.path.join(wine_script_path, "wine")
        with open(wine_script, "w") as f:
            f.write("""#!/bin/bash
# This is a simple wrapper for Wine that tries to find a working Wine installation

# Try to find system Wine
if command -v /usr/local/bin/wine &>/dev/null; then
    exec /usr/local/bin/wine "$@"
elif command -v /opt/homebrew/bin/wine &>/dev/null; then
    exec /opt/homebrew/bin/wine "$@"
elif command -v wine &>/dev/null; then
    exec wine "$@"
else
    echo "Wine not found. Please install Wine using: brew install --cask wine-stable"
    exit 1
fi
""")
        
        # Make the script executable
        os.chmod(wine_script, 0o755)
        
        # Try to download a portable Wine binary as a fallback
        try:
            print("Checking for system Wine...")
            # Check if Wine is already installed on the system
            try:
                subprocess.run(["which", "wine"], check=True, stdout=subprocess.PIPE)
                print("System Wine found. Using it.")
                return True
            except:
                print("System Wine not found.")
                
            # Try to download a portable Wine binary
            print("Downloading portable Wine binary...")
            # This is a simpler URL that should be more reliable
            wine_url = "https://github.com/Gcenx/winecx/releases/download/crossover-wine-22.1.1/wine-crossover-22.1.1-osx64.tar.xz"
            wine_archive = os.path.join(temp_dir, "wine.tar.xz")
            
            download_file(wine_url, wine_archive)
            
            # Extract the archive
            print("Extracting Wine...")
            try:
                # Extract with tar command which is more reliable
                subprocess.run(["tar", "-xf", wine_archive, "-C", wine_dir], check=True)
                print("Wine extracted successfully.")
                
                # Find the wine binary
                wine_binary = find_wine_binary(wine_dir)
                if wine_binary:
                    print(f"Wine binary found at: {wine_binary}")
                    
                    # Update the wine script to use our local binary
                    with open(wine_script, "w") as f:
                        f.write(f"""#!/bin/bash
# This is a wrapper for our local Wine installation
exec "{wine_binary}" "$@"
""")
                    
                    # Make sure it's executable
                    os.chmod(wine_script, 0o755)
                    return True
                else:
                    print("Wine binary not found in the extracted archive.")
            except Exception as e:
                print(f"Error extracting Wine with tar: {e}")
                
            # If we get here, we couldn't extract the archive with tar
            # Try using Python's tarfile module
            try:
                print("Trying alternative extraction method...")
                with tarfile.open(wine_archive) as tar:
                    tar.extractall(path=wine_dir)
                
                # Find the wine binary
                wine_binary = find_wine_binary(wine_dir)
                if wine_binary:
                    print(f"Wine binary found at: {wine_binary}")
                    
                    # Update the wine script to use our local binary
                    with open(wine_script, "w") as f:
                        f.write(f"""#!/bin/bash
# This is a wrapper for our local Wine installation
exec "{wine_binary}" "$@"
""")
                    
                    # Make sure it's executable
                    os.chmod(wine_script, 0o755)
                    return True
                else:
                    print("Wine binary not found in the extracted archive.")
            except Exception as e:
                print(f"Error extracting Wine with Python tarfile: {e}")
                
            # If all else fails, suggest manual installation
            print("Could not install Wine automatically.")
            print("Please install Wine manually using: brew install --cask wine-stable")
            print("Or download Wine from: https://wiki.winehq.org/MacOS")
            return False
                
        except Exception as e:
            print(f"Error downloading Wine: {e}")
            return False
            
        # If we get here, we at least have a script that will try to use system Wine
        print("Created Wine wrapper script. Please install Wine manually if needed.")
        return True

def find_wine_binary(directory):
    """Find the Wine binary in the extracted directory"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "wine" and not root.endswith("bin"):  # Skip our own script
                file_path = os.path.join(root, file)
                # Check if it's executable
                if os.access(file_path, os.X_OK):
                    return file_path
    return None

if __name__ == "__main__":
    install_wine() 