#!/usr/bin/env python3
"""
Wrapper script to run the Wine EXE Manager with proper environment settings
for macOS Sonoma 14.6 compatibility.
"""
import os
import sys
import subprocess

# Set environment variables for macOS compatibility
os.environ['SYSTEM_VERSION_COMPAT'] = '1'

# Print current directory for debugging
print(f"Current directory: {os.getcwd()}")

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
exe_manager_path = os.path.join(script_dir, "exe_manager.py")

# Check if exe_manager.py exists
if not os.path.exists(exe_manager_path):
    print(f"Error: Could not find {exe_manager_path}")
    sys.exit(1)

# Run the exe_manager.py script in a new process with the environment variable set
try:
    result = subprocess.run([sys.executable, exe_manager_path], 
                          env=os.environ, 
                          check=True)
    sys.exit(result.returncode)
except subprocess.CalledProcessError as e:
    print(f"Error running Wine EXE Manager: {e}")
    sys.exit(e.returncode)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1) 