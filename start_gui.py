#!/usr/bin/env python3

import subprocess
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def start_gui():
    # Determine the path to the GUI script
    gui_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "gui", "docker_manager_gui.py")

    # Get the absolute path to the project root
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Construct the command to set PYTHONPATH and run the GUI script
    # The user is expected to activate the virtual environment manually before running this script.
    command = f"export PYTHONPATH=$PYTHONPATH:{project_root} && python3 {gui_script}"

    logger.info(f"Starting DevEnvOps GUI...")
    logger.info(f"Command: {command}")

    try:
        # Execute the command using bash -c
        subprocess.run(["bash", "-c", command], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting GUI: {e}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        logger.error(f"Error: bash or python3 was not found. Ensure they are in your PATH.")
    except Exception as e:
        logger.exception(f"An unexpected error occurred")

if __name__ == "__main__":
    start_gui()