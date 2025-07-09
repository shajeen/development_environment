#!/usr/bin/env python3

import subprocess
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def start_web():
    # Get the absolute path to the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    web_app_script = os.path.join(project_root, "src", "web", "app.py")

    # Construct the command to set PYTHONPATH and run the web app
    # The user is expected to activate the virtual environment manually before running this script.
    command = f"export PYTHONPATH=$PYTHONPATH:{project_root} && python3 {web_app_script}"

    logger.info(f"Starting DevEnvOps Web Application...")
    logger.info(f"Command: {command}")
    logger.info(f"Open your browser and navigate to: http://localhost:5000")

    try:
        # Execute the command using bash -c
        subprocess.run(["bash", "-c", command], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting web application: {e}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        logger.error(f"Error: bash or python3 was not found. Ensure they are in your PATH.")
    except Exception as e:
        logger.exception(f"An unexpected error occurred")

if __name__ == "__main__":
    start_web()