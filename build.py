#!/usr/bin/env python3
"""
Build script for creating standalone executables for macOS, Windows, and Linux.
Usage:
    python build.py
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_dependencies():
    """Install build dependencies."""
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build():
    """Build the executable."""
    system = platform.system().lower()
    
    print(f"Building for {system}...")
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Build with PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "build.spec",
        "--clean",
        "--noconfirm",
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    # Determine executable name based on platform
    if system == "windows":
        exe_name = "lg-remote-api.exe"
    else:
        exe_name = "lg-remote-api"
    
    exe_path = Path("dist") / exe_name
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n✓ Build successful!")
        print(f"  Executable: {exe_path}")
        print(f"  Size: {size_mb:.2f} MB")
        print(f"\nTo run: ./dist/{exe_name}")
    else:
        print(f"\n✗ Build failed: {exe_path} not found")
        sys.exit(1)

def main():
    """Main entry point."""
    if not check_pyinstaller():
        print("PyInstaller not found. Installing...")
        install_dependencies()
    
    build()

if __name__ == "__main__":
    main()
