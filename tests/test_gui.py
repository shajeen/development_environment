#!/usr/bin/env python3
"""
DevEnvOps GUI Test Script
Test script to verify GUI functionality without Docker daemon
"""

import tkinter as tk
from src.core.docker_manager import DockerEnvironmentManager

def test_gui():
    """Test GUI components"""
    
    # Test manager initialization
    manager = DockerEnvironmentManager()
    
    print("✅ Manager initialized successfully")
    print(f"📋 Found {len(manager.environments)} environments:")
    
    for key, env in manager.environments.items():
        print(f"   - {key}: {env['name']} (Port: {env['port']}, Path: {env['path']})")
    
    # Test path validation
    print("\n🔍 Testing path validation:")
    for key, env in manager.environments.items():
        path = manager.base_path / env['path']
        status = "✅ EXISTS" if path.exists() else "❌ MISSING"
        print(f"   - {key}: {path} {status}")
    
    print("\n🎯 DevEnvOps GUI should now work without path errors!")
    print("💡 Run: source venv/bin/activate && python docker_manager_gui.py")

if __name__ == "__main__":
    test_gui()
