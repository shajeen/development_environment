#!/usr/bin/env python3

import subprocess
import os
import sys

def start_gui():
    # Determine the path to the virtual environment's activate script
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    activate_script = os.path.join(venv_path, "bin", "activate")

    # Determine the path to the GUI script
    gui_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "gui", "docker_manager_gui.py")

    # Construct the command to activate venv and run the GUI script
    # Use 'bash -c' to ensure the source command is executed correctly
    command = f"source {activate_script} && python3 {gui_script}"

    print(f"Starting DevEnvOps GUI...")
    print(f"Command: {command}")

    try:
        # Execute the command using bash -c
        # shell=False by default when passing a list, so bash will interpret the command string
        subprocess.run(["bash", "-c", command], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting GUI: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print(f"Error: bash was not found. Ensure bash is in your PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    start_gui()