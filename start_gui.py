#!/usr/bin/env python3

import subprocess
import os
import sys

def start_gui():
    # Determine the path to the GUI script
    gui_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "gui", "docker_manager_gui.py")

    # Get the absolute path to the project root
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Construct the command to set PYTHONPATH and run the GUI script
    # The user is expected to activate the virtual environment manually before running this script.
    command = f"export PYTHONPATH=$PYTHONPATH:{project_root} && python3 {gui_script}"

    print(f"Starting DevEnvOps GUI...")
    print(f"Command: {command}")

    try:
        # Execute the command using bash -c
        subprocess.run(["bash", "-c", command], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting GUI: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print(f"Error: bash or python3 was not found. Ensure they are in your PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    start_gui()