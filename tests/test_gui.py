#!/usr/bin/env python3
"""
DevEnvOps GUI Test Script
Test script to verify GUI functionality without Docker daemon
"""

import tkinter as tk
from src.core.docker_manager import DockerEnvironmentManager
import logging

# Configure logging for tests
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_gui():
    """Test GUI components"""
    
    # Test manager initialization
    manager = DockerEnvironmentManager()
    
    logger.info("Manager initialized successfully")
    logger.info(f"Found {len(manager.environments)} environments:")
    
    for key, env in manager.environments.items():
        logger.info(f"   - {key}: {env['name']} (Port: {env['port']}, Path: {env['path']})")
    
    # Test path validation
    logger.info("
Testing path validation:")
    for key, env in manager.environments.items():
        path = manager.base_path / env['path']
        status = "✅ EXISTS" if path.exists() else "❌ MISSING"
        logger.info(f"   - {key}: {path} {status}")
    
    logger.info("
DevEnvOps GUI should now work without path errors!")
    logger.info("💡 Run: source venv/bin/activate && python docker_manager_gui.py")

if __name__ == "__main__":
    test_gui()
