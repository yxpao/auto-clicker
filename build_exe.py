"""Build script to compile the application into a standalone Windows .exe."""

import os
import subprocess
import sys

def build():
    print("Building AutoClicker & Macro Studio Pro standalone executable...")
    
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconsole",                # Hide the terminal window
        "--onefile",                  # Pack everything into a single .exe
        "--name=AutoClickerStudio",   # Name of the output executable
        "--clean",                    # Clean cache before build
        "--paths=.",                  # Ensure root is in search path
        "main.py",
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        exe_path = os.path.abspath(os.path.join("dist", "AutoClickerStudio.exe"))
        print("\n" + "=" * 60)
        print(" BUILD SUCCESSFUL!")
        print(f" Executable created at: {exe_path}")
        print("=" * 60)
    else:
        print("\nBuild failed. Check the error log above.")

if __name__ == "__main__":
    build()
