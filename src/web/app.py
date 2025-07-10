#!/usr/bin/env python3
"""
Docker Development Environment Manager - Web Application
A web interface to manage Docker-based development environments
"""

import os
import sys
import json
import threading
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.docker_manager import DockerEnvironmentManager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-env-ops-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Global manager instance
manager = DockerEnvironmentManager()

# Status cache for performance
status_cache = {}
last_status_check = 0

# Container credentials storage (in-memory for now)
container_credentials = {}

def get_environment_status(env_key):
    """Get environment status with caching"""
    global status_cache
    
    current_time = time.time()
    cache_key = f"{env_key}"
    
    if (cache_key in status_cache and 
        current_time - status_cache[cache_key]['timestamp'] < 5):
        return status_cache[cache_key]['status']
    
    if env_key not in manager.environments:
        return "unknown"
    
    env = manager.environments[env_key]
    env_type = env.get("type", "docker-compose")
    env_path = str(manager.base_path / env["path"]) if env_type == "vagrant" else None
    
    status = manager.get_container_status(env["container"], env_type, env_path)
    status_cache[cache_key] = {'status': status, 'timestamp': current_time}
    
    return status

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/terminal')
def terminal():
    """Terminal page"""
    return render_template('terminal.html')

@socketio.on('execute_command')
def handle_execute_command(data):
    """Handle execute command request from terminal"""
    command = data['command']
    env_key = data.get('env_key') # Optional: if command needs to run in an environment's context
    
    logger.info(f"Received execute_command request: {command}")
    
    def command_worker():
        try:
            # Determine the working directory for the command
            cwd = None
            if env_key and env_key in manager.environments:
                env = manager.environments[env_key]
                env_path = manager.base_path / "templates" / env["path"]
                if env_path.exists():
                    cwd = str(env_path)
                else:
                    socketio.emit('terminal_output', {'output': f'❌ Environment path not found: {env_path}'})
                    socketio.emit('command_finished', {'success': False})
                    return
            
            success = run_terminal_command(command, cwd=cwd)
            socketio.emit('command_finished', {'success': success})
        except Exception as e:
            logger.exception(f"Terminal command error: {command}")
            socketio.emit('terminal_output', {'output': f'❌ Error executing command: {str(e)}'})
            socketio.emit('command_finished', {'success': False})
            
    thread = threading.Thread(target=command_worker)
    thread.daemon = True
    thread.start()

def run_terminal_command(command: str, cwd: str = None) -> bool:
    """Run a shell command and stream output to the terminal"""
    try:
        import subprocess
        import os
        
        socketio.emit('terminal_output', {'output': f'\n$ {command}\n'})
        
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        
        process = subprocess.Popen(
            command,
            shell=True, # Execute command as a shell command
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=cwd,
            bufsize=0,
            env=env
        )
        
        while True:
            line = process.stdout.readline()
            if line:
                socketio.emit('terminal_output', {'output': line})
            elif process.poll() is not None:
                break
        
        returncode = process.returncode
        if returncode != 0:
            socketio.emit('terminal_output', {'output': f'Command exited with code {returncode}\n'})
            return False
        return True
        
    except Exception as e:
        logger.exception(f"Error in run_terminal_command: {command}")
        socketio.emit('terminal_output', {'output': f'Error: {str(e)}\n'})
        return False

@socketio.on('build_environment')

@app.route('/api/environments')
def get_environments():
    """Get all environments with their status"""
    manager.load_environments()
    
    environments = []
    for key, env in manager.environments.items():
        env_info = {
            'key': key,
            'name': env['name'],
            'type': env.get('type', 'docker-compose'),
            'status': get_environment_status(key),
            'port': env['port'],
            'container': env['container'],
            'image': env['image'],
            'volume': env.get('volume', 'N/A'),
            'description': env.get('description', 'No description available'),
            'path': env['path']
        }
        environments.append(env_info)
    
    return jsonify(environments)

@app.route('/api/environment/<env_key>')
def get_environment(env_key):
    """Get specific environment details"""
    if env_key not in manager.environments:
        return jsonify({'error': 'Environment not found'}), 404
    
    env = manager.environments[env_key]
    env_type = env.get("type", "docker-compose")
    
    env_info = {
        'key': env_key,
        'name': env['name'],
        'type': env_type,
        'status': get_environment_status(env_key),
        'port': env['port'],
        'container': env['container'],
        'image': env['image'],
        'volume': env.get('volume', 'N/A'),
        'description': env.get('description', 'No description available'),
        'path': env['path']
    }
    
    # Add SSH command and credentials
    if env_type == "vagrant":
        ssh_user = env.get("ssh_user", "root")
        env_info['ssh_command'] = f"ssh {ssh_user}@localhost -p {env['port']}"
        if env.get("ssh_key"):
            env_info['credentials'] = f"SSH Key: {env['ssh_key']}"
        else:
            env_info['credentials'] = "SSH Key required"
        
        if env.get("vnc_port"):
            env_info['ssh_command'] += f" | VNC: 127.0.0.1:{env['vnc_port']}"
        
        if env.get("gpu_support"):
            env_info['credentials'] += " | GPU: Enabled"
    else:
        env_info['ssh_command'] = f"ssh dev@localhost -p {env['port']}"
        env_info['credentials'] = "Use the Credentials button to set username/password"
    
    return jsonify(env_info)

@socketio.on('build_environment')
def handle_build_environment(data):
    """Handle build environment request"""
    env_key = data['env_key']
    no_cache = data.get('no_cache', False)
    
    logger.info(f"Received build_environment request for {env_key}, no_cache={no_cache}")
    
    # Initial status message with detailed info
    emit('output', {'message': f'🎯 Build request received for environment: {env_key}'})
    emit('output', {'message': f'⚙️ Build options:'})
    emit('output', {'message': f'   - Environment: {env_key}'})
    emit('output', {'message': f'   - No cache: {"Yes" if no_cache else "No"}'})
    emit('output', {'message': f'   - Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}'})
    emit('output', {'message': f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'})
    
    def build_worker():
        try:
            logger.info(f"Starting build for {env_key}")
            success = build_environment_with_output(env_key, no_cache)
            
            # Final status
            if success:
                socketio.emit('output', {'message': f'🎉 Build process completed successfully!'})
                socketio.emit('output', {'message': f'✅ Environment {env_key} is ready to start'})
            else:
                socketio.emit('output', {'message': f'💥 Build process failed!'})
                socketio.emit('output', {'message': f'❌ Please check the output above for errors'})
            
            logger.info(f"Build completed for {env_key}, success={success}")
            socketio.emit('refresh_status')
        except Exception as e:
            logger.exception(f"Build error for {env_key}")
            socketio.emit('output', {'message': f'❌ Unexpected build error: {str(e)}'})
            socketio.emit('output', {'message': f'🔍 This is likely a system or configuration issue'})
    
    thread = threading.Thread(target=build_worker)
    thread.daemon = True
    thread.start()

def build_environment_with_output(env_key: str, no_cache: bool = False):
    """Build environment with real-time output streaming"""
    # Initial progress update
    socketio.emit('progress_update', {
        'percentage': 5,
        'label': f'Initializing build for {env_key}',
        'status': 'Initializing'
    })
    
    socketio.emit('output', {'message': f'🔍 Starting build process for environment: {env_key}'})
    
    if env_key not in manager.environments:
        socketio.emit('output', {'message': f'❌ Environment {env_key} not found in configuration'})
        return False
    
    env = manager.environments[env_key]
    env_path = manager.base_path / "templates" / env["path"]
    socketio.emit('output', {'message': f'📁 Environment template path: {env_path}'})
    socketio.emit('output', {'message': f'🏷️ Environment type: {env.get("type", "docker-compose")}'})
    socketio.emit('output', {'message': f'🖼️ Target image: {env["image"]}'})
    
    if not env_path.exists():
        socketio.emit('output', {'message': f'❌ Environment path does not exist: {env_path}'})
        return False
    
    socketio.emit('output', {'message': f'✅ Environment template found and accessible'})
    
    # Show build options
    if no_cache:
        socketio.emit('output', {'message': f'🚫 Building with --no-cache option (fresh build)'})
    else:
        socketio.emit('output', {'message': f'🔄 Building with cache (faster build if layers exist)'})
    
    # Update progress after validation
    socketio.emit('progress_update', {
        'percentage': 10,
        'label': 'Environment validated, starting build...',
        'status': 'Validated'
    })
    
    if env.get("type") == "vagrant":
        socketio.emit('output', {'message': f'🗺️ Processing Vagrant environment build...'})
        
        # For Vagrant environments, build the Docker image first
        dockerfile_path = env_path / "Dockerfile"
        socketio.emit('output', {'message': f'🔍 Checking for Dockerfile at: {dockerfile_path}'})
        
        if dockerfile_path.exists():
            socketio.emit('output', {'message': f'✅ Dockerfile found, building Docker image for Vagrant'})
            socketio.emit('output', {'message': f'🐳 Building Docker image: {env["image"]}'})
            cmd = ["docker", "build", "-t", env["image"], "."]
            if no_cache:
                cmd.append("--no-cache")
            
            socketio.emit('output', {'message': f'🔧 Docker build command: {" ".join(cmd)}'})
            return run_command_with_output(cmd, str(env_path))
        else:
            socketio.emit('output', {'message': f'ℹ️ No Dockerfile found at {dockerfile_path}'})
            socketio.emit('output', {'message': f'✅ Vagrant environment ready (no Docker build required)'})
            return True
    else:
        socketio.emit('output', {'message': f'🐳 Processing Docker Compose environment build...'})
        
        # Check for docker-compose.yaml
        compose_file = env_path / "docker-compose.yaml"
        if compose_file.exists():
            socketio.emit('output', {'message': f'✅ Found docker-compose.yaml at: {compose_file}'})
        else:
            socketio.emit('output', {'message': f'⚠️ docker-compose.yaml not found at: {compose_file}'})
        
        # Docker Compose environments
        cmd = ["docker-compose", "build"]
        if no_cache:
            cmd.append("--no-cache")
        
        socketio.emit('output', {'message': f'🔧 Docker Compose build command: {" ".join(cmd)}'})
        return run_command_with_output_and_credentials(cmd, str(env_path), env_key)

def format_vagrant_output(line):
    """Format Vagrant output with appropriate icons and colors"""
    line = line.strip()
    
    # Vagrant progress indicators
    if "Bringing machine" in line:
        return f"🚀 {line}"
    elif "Checking if box" in line:
        return f"📦 {line}"
    elif "Box 'virtualbox'" in line or "downloading" in line.lower():
        return f"⬇️ {line}"
    elif "Configuring and enabling network interfaces" in line:
        return f"🌐 {line}"
    elif "Mounting shared folders" in line:
        return f"📁 {line}"
    elif "Machine booted and ready" in line:
        return f"✅ {line}"
    elif "Forcing shutdown" in line or "Destroying" in line:
        return f"🗑️ {line}"
    elif "error" in line.lower() or "failed" in line.lower():
        return f"❌ {line}"
    elif "warning" in line.lower() or "warn" in line.lower():
        return f"⚠️ {line}"
    else:
        return f"🗺️ {line}"

def run_command_with_output(cmd, cwd=None):
    """Run command and stream ALL output (stdout + stderr) to web interface"""
    try:
        import subprocess
        import os
        
        socketio.emit('output', {'message': f'🚀 Executing command: {" ".join(cmd)}'})
        socketio.emit('output', {'message': f'📂 Working directory: {cwd}'})
        
        # Set environment variables to disable buffering
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        env['DOCKER_BUILDKIT'] = '0'  # Disable BuildKit for more verbose output
        env['COMPOSE_DOCKER_CLI_BUILD'] = '0'  # Use classic docker build
        
        # Vagrant-specific environment variables
        if cmd and cmd[0] == 'vagrant':
            env['VAGRANT_NO_COLOR'] = '1'  # Disable color output for cleaner logs
            env['VAGRANT_LOG'] = 'info'  # Set log level to info
            socketio.emit('output', {'message': f'🗺️ Vagrant-specific environment variables set:'})
            socketio.emit('output', {'message': f'   - VAGRANT_NO_COLOR=1 (cleaner output)'})
            socketio.emit('output', {'message': f'   - VAGRANT_LOG=info (detailed logging)'})
        
        socketio.emit('output', {'message': f'🔄 Starting process...'})
        socketio.emit('output', {'message': f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'})
        
        # Use a simpler approach that combines stdout and stderr
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr with stdout
            universal_newlines=True,
            cwd=cwd,
            bufsize=0,  # Unbuffered
            env=env
        )
        socketio.emit('output', {'message': f'🔢 Process started with PID: {process.pid}'})
        
        line_count = 0
        
        # Initial progress for command execution
        socketio.emit('progress_update', {
            'percentage': 20,
            'label': 'Command execution started...',
            'status': 'Running'
        })
        
        # Read output line by line in real-time
        while True:
            line = process.stdout.readline()
            if line:
                line_count += 1
                line_content = line.rstrip()
                
                try:
                    # Add better formatting for different command types
                    if cmd and cmd[0] == 'vagrant':
                        # Format Vagrant-specific output
                        formatted_line = format_vagrant_output(line_content)
                        socketio.emit('output', {'message': formatted_line})
                        socketio.emit('terminal_output', {'output': formatted_line + '\n'})
                    elif cmd and cmd[0] == 'docker-compose':
                        # Format Docker Compose specific output with progress tracking
                        if 'Building' in line_content:
                            socketio.emit('progress_update', {
                                'percentage': 10,
                                'label': 'Building Docker Compose services...',
                                'status': 'Building'
                            })
                            socketio.emit('output', {'message': f'🔨 {line_content}'})
                            socketio.emit('terminal_output', {'output': f'🔨 {line_content}\n'})
                        elif 'Pulling' in line_content:
                            socketio.emit('progress_update', {
                                'percentage': 30,
                                'label': 'Pulling Docker images...',
                                'status': 'Pulling'
                            })
                            socketio.emit('output', {'message': f'⬇️ {line_content}'})
                            socketio.emit('terminal_output', {'output': f'⬇️ {line_content}\n'})
                        elif 'Creating' in line_content:
                            socketio.emit('progress_update', {
                                'percentage': 60,
                                'label': 'Creating containers...',
                                'status': 'Creating'
                            })
                            socketio.emit('output', {'message': f'🏗️ {line_content}'})
                            socketio.emit('terminal_output', {'output': f'🏗️ {line_content}\n'})
                        elif 'Starting' in line_content:
                            socketio.emit('progress_update', {
                                'percentage': 80,
                                'label': 'Starting containers...',
                                'status': 'Starting'
                            })
                            socketio.emit('output', {'message': f'🚀 {line_content}'})
                            socketio.emit('terminal_output', {'output': f'🚀 {line_content}\n'})
                        elif 'Stopping' in line_content:
                            socketio.emit('progress_update', {
                                'percentage': 50,
                                'label': 'Stopping containers...',
                                'status': 'Stopping'
                            })
                            socketio.emit('output', {'message': f'🛑 {line_content}'})
                            socketio.emit('terminal_output', {'output': f'🛑 {line_content}\n'})
                        elif 'Removing' in line_content:
                            socketio.emit('progress_update', {
                                'percentage': 75,
                                'label': 'Removing containers...',
                                'status': 'Removing'
                            })
                            socketio.emit('output', {'message': f'🗑️ {line_content}'})
                            socketio.emit('terminal_output', {'output': f'🗑️ {line_content}\n'})
                        elif 'done' in line_content.lower() or 'complete' in line_content.lower():
                            socketio.emit('progress_update', {
                                'percentage': 100,
                                'label': 'Operation completed!',
                                'status': 'Complete'
                            })
                            socketio.emit('output', {'message': f'✅ {line_content}'})
                            socketio.emit('terminal_output', {'output': f'✅ {line_content}\n'})
                        elif 'error' in line_content.lower() or 'failed' in line_content.lower():
                            socketio.emit('output', {'message': f'❌ {line_content}'})
                            socketio.emit('terminal_output', {'output': f'❌ {line_content}\n'})
                        else:
                            socketio.emit('output', {'message': f'📤 {line_content}'})
                            socketio.emit('terminal_output', {'output': f'📤 {line_content}\n'})
                    else:
                        socketio.emit('output', {'message': f'📤 {line_content}'})
                        socketio.emit('terminal_output', {'output': f'📤 {line_content}\n'})
                        
                except Exception as emit_error:
                    socketio.emit('output', {'message': f'⚠️ Error displaying output: {str(emit_error)}'})
                    socketio.emit('terminal_output', {'output': f'⚠️ Error displaying output: {str(emit_error)}\n'})
                    
            elif process.poll() is not None:
                break
        
        returncode = process.returncode
        socketio.emit('output', {'message': f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'})
        socketio.emit('output', {'message': f'📊 Command execution summary:'})
        socketio.emit('output', {'message': f'   - Command: {" ".join(cmd)}'})
        socketio.emit('output', {'message': f'   - Exit code: {returncode}'})
        socketio.emit('output', {'message': f'   - Output lines: {line_count}'})
        socketio.emit('output', {'message': f'   - Result: {"✅ Success" if returncode == 0 else "❌ Failed"}'})
        
        socketio.emit('terminal_output', {'output': f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'})
        socketio.emit('terminal_output', {'output': f'📊 Command execution summary:\n'})
        socketio.emit('terminal_output', {'output': f'   - Command: {" ".join(cmd)}\n'})
        socketio.emit('terminal_output', {'output': f'   - Exit code: {returncode}\n'})
        socketio.emit('terminal_output', {'output': f'   - Output lines: {line_count}\n'})
        socketio.emit('terminal_output', {'output': f'   - Result: {"✅ Success" if returncode == 0 else "❌ Failed"}\n'})
        
        # Final progress update
        if returncode == 0:
            socketio.emit('progress_update', {
                'percentage': 100,
                'label': 'Command completed successfully!',
                'status': 'Complete'
            })
        else:
            socketio.emit('progress_update', {
                'percentage': 0,
                'label': f'Command failed (exit code: {returncode})',
                'status': 'Failed'
            })
        
        return returncode == 0
        
    except Exception as e:
        logger.exception(f"Command error")
        socketio.emit('output', {'message': f'❌ Command error: {str(e)}'})
        socketio.emit('progress_update', {
            'percentage': 0,
            'label': 'Command failed due to error',
            'status': 'Error'
        })
        socketio.emit('terminal_output', {'output': f'❌ Command error: {str(e)}\n'})
        return False

def run_command_with_output_and_credentials(cmd, cwd=None, env_key=None):
    """Run command with credentials and stream output"""
    try:
        import subprocess
        import os
        
        socketio.emit('output', {'message': f'🚀 Executing command: {" ".join(cmd)}'})
        socketio.emit('output', {'message': f'📂 Working directory: {cwd}'})
        
        # Set environment variables to disable buffering
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        env['DOCKER_BUILDKIT'] = '0'  # Disable BuildKit for more verbose output
        env['COMPOSE_DOCKER_CLI_BUILD'] = '0'  # Use classic docker build
        
        socketio.emit('output', {'message': f'⚙️ Environment variables set:'})
        socketio.emit('output', {'message': f'   - PYTHONUNBUFFERED=1 (for real-time output)'})
        socketio.emit('output', {'message': f'   - DOCKER_BUILDKIT=0 (classic build for verbose output)'})
        socketio.emit('output', {'message': f'   - COMPOSE_DOCKER_CLI_BUILD=0 (classic docker build)'})
        
        # Add credentials if available
        if env_key and env_key in container_credentials:
            credentials = container_credentials[env_key]
            env['DEV_PASSWORD'] = credentials['password']
            socketio.emit('output', {'message': f'🔑 Using custom credentials for user: {credentials["username"]}'})
            socketio.emit('output', {'message': f'🔐 Password length: {len(credentials["password"])} characters'})
        else:
            env['DEV_PASSWORD'] = 'devpass'
            socketio.emit('output', {'message': f'🔑 Using default credentials (username: dev, password: devpass)'})
        
        socketio.emit('output', {'message': f'🔄 Starting process...'})
        socketio.emit('output', {'message': f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'})
        
        # Use a simpler approach that combines stdout and stderr
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr with stdout
            universal_newlines=True,
            cwd=cwd,
            bufsize=0,  # Unbuffered
            env=env
        )
        socketio.emit('output', {'message': f'🔢 Process started with PID: {process.pid}'})
        
        line_count = 0
        # Track progress for Docker builds
        total_steps = 1
        current_step = 0
        
        # Initial progress for command execution (starting at 15% since we're past validation)
        socketio.emit('progress_update', {
            'percentage': 15,
            'label': 'Starting command execution...',
            'status': 'Executing'
        })
        
        # Read output line by line in real-time
        while True:
            line = process.stdout.readline()
            if line:
                line_count += 1
                line_content = line.rstrip()
                
                # Progress tracking for Docker builds
                # Handle both old format "Step X/Y" and new format "#X [service Y/Z]"
                docker_step_match = None
                if 'Step' in line_content and '/' in line_content:
                    # Old format: "Step 1/15 :"
                    try:
                        import re
                        docker_step_match = re.search(r'Step (\d+)/(\d+)', line_content)
                    except:
                        pass
                elif '#' in line_content and '[' in line_content and '/' in line_content:
                    # New format: "#6 [python_workspace 2/9] RUN apt-get update"
                    try:
                        import re
                        docker_step_match = re.search(r'#\d+\s+\[.*?\s+(\d+)/(\d+)\]', line_content)
                    except:
                        pass
                
                if docker_step_match:
                    try:
                        current_step = int(docker_step_match.group(1))
                        total_steps = int(docker_step_match.group(2))
                        progress_percentage = int((current_step / total_steps) * 100)
                        
                        # Adjust percentage to start from 20% (since we already used 15% for initialization)
                        adjusted_percentage = 20 + int((progress_percentage * 0.7))  # Scale to 20-90%
                        
                        # Update progress bar
                        socketio.emit('progress_update', {
                            'percentage': adjusted_percentage,
                            'label': f'Building step {current_step} of {total_steps}',
                            'status': f'Step {current_step}/{total_steps}'
                        })
                        socketio.emit('output', {'message': f'🏗️ {line_content}'})
                        socketio.emit('terminal_output', {'output': f'🏗️ {line_content}\n'})
                    except Exception as e:
                        socketio.emit('output', {'message': f'🏗️ {line_content}'})
                        socketio.emit('terminal_output', {'output': f'🏗️ {line_content}\n'})
                    
                elif 'FROM' in line_content and line_content.startswith('FROM'):
                    socketio.emit('output', {'message': f'📦 {line_content}'})
                    socketio.emit('terminal_output', {'output': f'📦 {line_content}\n'})
                elif 'RUN' in line_content and line_content.startswith('RUN'):
                    socketio.emit('output', {'message': f'⚡ {line_content}'})
                    socketio.emit('terminal_output', {'output': f'⚡ {line_content}\n'})
                elif 'COPY' in line_content and line_content.startswith('COPY'):
                    socketio.emit('output', {'message': f'📋 {line_content}'})
                    socketio.emit('terminal_output', {'output': f'📋 {line_content}\n'})
                elif 'Successfully built' in line_content:
                    socketio.emit('progress_update', {
                        'percentage': 90,
                        'label': 'Build completed, tagging image...',
                        'status': 'Tagging'
                    })
                    socketio.emit('output', {'message': f'🎉 {line_content}'})
                    socketio.emit('terminal_output', {'output': f'🎉 {line_content}\n'})
                elif 'Successfully tagged' in line_content:
                    socketio.emit('progress_update', {
                        'percentage': 100,
                        'label': 'Build completed successfully!',
                        'status': 'Complete'
                    })
                    socketio.emit('output', {'message': f'🏷️ {line_content}'})
                    socketio.emit('terminal_output', {'output': f'🏷️ {line_content}\n'})
                elif 'Built' in line_content and (line_content.strip().endswith('Built') or 'Built' == line_content.strip()):
                    # Docker Compose build completion: " python_workspace  Built"
                    socketio.emit('progress_update', {
                        'percentage': 100,
                        'label': 'Build completed successfully!',
                        'status': 'Complete'
                    })
                    socketio.emit('output', {'message': f'🎉 {line_content}'})
                    socketio.emit('terminal_output', {'output': f'🎉 {line_content}\n'})
                elif 'exporting to image' in line_content:
                    socketio.emit('progress_update', {
                        'percentage': 95,
                        'label': 'Exporting Docker image...',
                        'status': 'Exporting'
                    })
                    socketio.emit('output', {'message': f'📤 {line_content}'})
                    socketio.emit('terminal_output', {'output': f'📤 {line_content}\n'})
                elif 'writing image' in line_content and 'done' in line_content:
                    socketio.emit('progress_update', {
                        'percentage': 98,
                        'label': 'Finalizing image...',
                        'status': 'Finalizing'
                    })
                    socketio.emit('output', {'message': f'✍️ {line_content}'})
                    socketio.emit('terminal_output', {'output': f'✍️ {line_content}\n'})
                elif 'ERROR' in line_content.upper() or 'FAILED' in line_content.upper():
                    socketio.emit('output', {'message': f'❌ {line_content}'})
                    socketio.emit('terminal_output', {'output': f'❌ {line_content}\n'})
                elif 'WARNING' in line_content.upper() or 'WARN' in line_content.upper():
                    socketio.emit('output', {'message': f'⚠️ {line_content}'})
                    socketio.emit('terminal_output', {'output': f'⚠️ {line_content}\n'})
                elif '-->' in line_content:
                    socketio.emit('output', {'message': f'📤 {line_content}'})
                    socketio.emit('terminal_output', {'output': f'📤 {line_content}\n'})
                else:
                    socketio.emit('output', {'message': f'📤 {line_content}'})
                    socketio.emit('terminal_output', {'output': f'📤 {line_content}\n'})
                
            elif process.poll() is not None:
                break
        
        returncode = process.returncode
        socketio.emit('output', {'message': f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'})
        socketio.emit('output', {'message': f'📊 Process completed:'})
        socketio.emit('output', {'message': f'   - Exit code: {returncode}'})
        socketio.emit('output', {'message': f'   - Output lines processed: {line_count}'})
        socketio.emit('output', {'message': f'   - Success: {"✅ Yes" if returncode == 0 else "❌ No"}'})
        
        socketio.emit('terminal_output', {'output': f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'})
        socketio.emit('terminal_output', {'output': f'📊 Process completed:\n'})
        socketio.emit('terminal_output', {'output': f'   - Exit code: {returncode}\n'})
        socketio.emit('terminal_output', {'output': f'   - Output lines processed: {line_count}\n'})
        socketio.emit('terminal_output', {'output': f'   - Success: {"✅ Yes" if returncode == 0 else "❌ No"}\n'})
        
        if returncode == 0:
            socketio.emit('output', {'message': f'🎉 Build completed successfully!'})
            # Only emit 100% if it wasn't already emitted by "Successfully tagged"
            if current_step == 0:  # No Docker steps were detected
                socketio.emit('progress_update', {
                    'percentage': 100,
                    'label': 'Build completed successfully!',
                    'status': 'Complete'
                })
        else:
            socketio.emit('output', {'message': f'💥 Build failed with exit code {returncode}'})
            socketio.emit('progress_update', {
                'percentage': 0,
                'label': f'Build failed (exit code: {returncode})',
                'status': 'Failed'
            })
            
        return returncode == 0
        
    except Exception as e:
        logger.exception(f"Command error")
        socketio.emit('output', {'message': f'❌ Command error: {str(e)}'})
        socketio.emit('progress_update', {
            'percentage': 0,
            'label': 'Build failed due to error',
            'status': 'Error'
        })
        socketio.emit('terminal_output', {'output': f'❌ Command error: {str(e)}\n'})
        return False

@socketio.on('start_environment')
def handle_start_environment(data):
    """Handle start environment request"""
    env_key = data['env_key']
    
    emit('output', {'message': f'Starting {env_key} environment...'})
    
    def start_worker():
        try:
            success = start_environment_with_output(env_key)
            if success:
                env = manager.environments[env_key]
                env_type = env.get("type", "docker-compose")
                socketio.emit('output', {'message': f'✅ {env_key} started successfully!'})
                
                if env_type == "vagrant":
                    ssh_user = env.get("ssh_user", "root")
                    socketio.emit('output', {'message': f'📡 SSH: ssh {ssh_user}@localhost -p {env["port"]}'})
                    if env.get("ssh_key"):
                        socketio.emit('output', {'message': f'🔑 SSH Key: {env["ssh_key"]}'})
                    if env.get("vnc_port"):
                        socketio.emit('output', {'message': f'🗺 VNC: Connect to 127.0.0.1:{env["vnc_port"]}'})
                else:
                    socketio.emit('output', {'message': f'📡 SSH: ssh dev@localhost -p {env["port"]}'})
                    socketio.emit('output', {'message': f'🔑 Credentials: Use the Credentials button to set username/password'})
            else:
                socketio.emit('output', {'message': f'❌ Failed to start {env_key} environment!'})
            
            socketio.emit('refresh_status')
        except Exception as e:
            socketio.emit('output', {'message': f'❌ Start error: {str(e)}'})
    
    thread = threading.Thread(target=start_worker)
    thread.daemon = True
    thread.start()

def start_environment_with_output(env_key: str):
    """Start environment with real-time output streaming"""
    # Initial progress update
    socketio.emit('progress_update', {
        'percentage': 5,
        'label': f'Initializing startup for {env_key}',
        'status': 'Initializing'
    })
    
    socketio.emit('output', {'message': f'🚀 Starting environment: {env_key}'})
    socketio.emit('terminal_output', {'output': f'🚀 Starting environment: {env_key}\n'})
    
    if env_key not in manager.environments:
        socketio.emit('output', {'message': f'❌ Environment {env_key} not found in configuration'})
        socketio.emit('terminal_output', {'output': f'❌ Environment {env_key} not found in configuration\n'})
        return False
    
    env = manager.environments[env_key]
    env_path = manager.base_path / "templates" / env["path"]
    
    socketio.emit('output', {'message': f'📁 Environment path: {env_path}'})
    socketio.emit('output', {'message': f'🏷️ Environment type: {env.get("type", "docker-compose")}'})
    socketio.emit('output', {'message': f'🌐 Target port: {env["port"]}'})
    socketio.emit('output', {'message': f'📦 Container name: {env["container"]}'})
    socketio.emit('terminal_output', {'output': f'📁 Environment path: {env_path}\n'})
    socketio.emit('terminal_output', {'output': f'🏷️ Environment type: {env.get("type", "docker-compose")}\n'})
    socketio.emit('terminal_output', {'output': f'🌐 Target port: {env["port"]}\n'})
    socketio.emit('terminal_output', {'output': f'📦 Container name: {env["container"]}\n'})
    
    # Update progress after validation
    socketio.emit('progress_update', {
        'percentage': 15,
        'label': 'Environment validated, preparing to start...',
        'status': 'Validated'
    })
    
    if env.get("type") == "vagrant":
        # For Vagrant environments
        if not env_path.exists():
            socketio.emit('output', {'message': f'❌ Environment path does not exist: {env_path}'})
            return False
        
        socketio.emit('output', {'message': f'🗺️ Processing Vagrant environment startup...'})
        socketio.emit('output', {'message': f'🔍 Using VirtualBox provider'})
        socketio.emit('terminal_output', {'output': f'🗺️ Processing Vagrant environment startup...\n'})
        socketio.emit('terminal_output', {'output': f'🔍 Using VirtualBox provider\n'})
        
        # Check for Vagrantfile
        vagrantfile = env_path / "Vagrantfile"
        if vagrantfile.exists():
            socketio.emit('output', {'message': f'✅ Vagrantfile found at: {vagrantfile}'})
        else:
            socketio.emit('output', {'message': f'❌ Vagrantfile not found at: {vagrantfile}'})
            return False
        
        cmd = ["vagrant", "up", "--provider=virtualbox"]
        socketio.emit('output', {'message': f'🔧 Vagrant command: {" ".join(cmd)}'})
        socketio.emit('terminal_output', {'output': f'🔧 Vagrant command: {" ".join(cmd)}\n'})
        return run_command_with_output(cmd, str(env_path))
    else:
        # Docker Compose environments
        socketio.emit('output', {'message': f'🐳 Processing Docker Compose environment startup...'})
        socketio.emit('terminal_output', {'output': f'🐳 Processing Docker Compose environment startup...\n'})
        
        # Check for docker-compose.yaml
        compose_file = env_path / "docker-compose.yaml"
        if compose_file.exists():
            socketio.emit('output', {'message': f'✅ Found docker-compose.yaml at: {compose_file}'})
            socketio.emit('terminal_output', {'output': f'✅ Found docker-compose.yaml at: {compose_file}\n'})
        else:
            socketio.emit('output', {'message': f'❌ docker-compose.yaml not found at: {compose_file}'})
            socketio.emit('terminal_output', {'output': f'❌ docker-compose.yaml not found at: {compose_file}\n'})
            return False
        
        cmd = ["docker-compose", "up", "-d"]
        socketio.emit('output', {'message': f'🔧 Docker Compose command: {" ".join(cmd)}'})
        socketio.emit('output', {'message': f'🔄 Starting in detached mode (-d flag)'})
        socketio.emit('terminal_output', {'output': f'🔧 Docker Compose command: {" ".join(cmd)}\n'})
        socketio.emit('terminal_output', {'output': f'🔄 Starting in detached mode (-d flag)\n'})
        
        return run_command_with_output_and_credentials(cmd, str(env_path), env_key)

@socketio.on('stop_environment')
def handle_stop_environment(data):
    """Handle stop environment request"""
    env_key = data['env_key']
    
    emit('output', {'message': f'Stopping {env_key} environment...'})
    
    def stop_worker():
        try:
            success = stop_environment_with_output(env_key)
            status = f"✅ {env_key} stopped successfully!" if success else f"❌ Failed to stop {env_key}!"
            socketio.emit('output', {'message': status})
            socketio.emit('refresh_status')
        except Exception as e:
            socketio.emit('output', {'message': f'❌ Stop error: {str(e)}'})
    
    thread = threading.Thread(target=stop_worker)
    thread.daemon = True
    thread.start()

def stop_environment_with_output(env_key: str):
    """Stop environment with real-time output streaming"""
    if env_key not in manager.environments:
        return False
    
    env = manager.environments[env_key]
    env_path = manager.base_path / "templates" / env["path"]
    
    if env.get("type") == "vagrant":
        # For Vagrant environments
        if not env_path.exists():
            socketio.emit('output', {'message': f'❌ Environment path does not exist: {env_path}'})
            return False
        
        socketio.emit('output', {'message': f'🗺️ Stopping Vagrant environment...'})
        socketio.emit('terminal_output', {'output': f'🗺️ Stopping Vagrant environment...\n'})
        cmd = ["vagrant", "halt"]
        return run_command_with_output(cmd, str(env_path))
    else:
        # Docker Compose environments
        socketio.emit('output', {'message': f'🐳 Stopping Docker Compose environment...\n'})
        socketio.emit('terminal_output', {'output': f'🐳 Stopping Docker Compose environment...\n'})
        cmd = ["docker-compose", "down"]
        return run_command_with_output(cmd, str(env_path))

@socketio.on('restart_environment')
def handle_restart_environment(data):
    """Handle restart environment request"""
    env_key = data['env_key']
    
    emit('output', {'message': f'🔄 Restarting {env_key} environment...'})
    
    def restart_worker():
        try:
            # Stop first
            socketio.emit('output', {'message': f'🛑 Stopping {env_key} environment...'})
            stop_success = stop_environment_with_output(env_key)
            if stop_success:
                socketio.emit('output', {'message': f'✅ {env_key} stopped successfully!'})
            
            # Start
            socketio.emit('output', {'message': f'🚀 Starting {env_key} environment...'})
            start_success = start_environment_with_output(env_key)
            if start_success:
                env = manager.environments[env_key]
                env_type = env.get("type", "docker-compose")
                socketio.emit('output', {'message': f'✅ {env_key} started successfully!'})
                
                if env_type == "vagrant":
                    ssh_user = env.get("ssh_user", "root")
                    socketio.emit('output', {'message': f'📡 SSH: ssh {ssh_user}@localhost -p {env["port"]}'})
                    if env.get("ssh_key"):
                        socketio.emit('output', {'message': f'🔑 SSH Key: {env["ssh_key"]}'})
                    if env.get("vnc_port"):
                        socketio.emit('output', {'message': f'🗺 VNC: Connect to 127.0.0.1:{env["vnc_port"]}'})
                else:
                    socketio.emit('output', {'message': f'📡 SSH: ssh dev@localhost -p {env["port"]}'})
                    socketio.emit('output', {'message': f'🔑 Credentials: Use the Credentials button to set username/password'})
            else:
                socketio.emit('output', {'message': f'❌ Failed to start {env_key} environment!'})
            
            socketio.emit('refresh_status')
        except Exception as e:
            socketio.emit('output', {'message': f'❌ Restart error: {str(e)}'})
    
    thread = threading.Thread(target=restart_worker)
    thread.daemon = True
    thread.start()

@socketio.on('clear_environment')
def handle_clear_environment(data):
    """Handle clear environment request"""
    env_key = data['env_key']
    remove_volumes = data.get('remove_volumes', False)
    
    emit('output', {'message': f'Clearing {env_key} environment...'})
    
    def clear_worker():
        try:
            success = clear_environment_with_output(env_key, remove_volumes)
            status = f"✅ {env_key} cleared successfully!" if success else f"❌ Failed to clear {env_key}!"
            socketio.emit('output', {'message': status})
            socketio.emit('refresh_status')
        except Exception as e:
            socketio.emit('output', {'message': f'❌ Clear error: {str(e)}'})
    
    thread = threading.Thread(target=clear_worker)
    thread.daemon = True
    thread.start()

def clear_environment_with_output(env_key: str, remove_volumes: bool = False):
    """Clear environment with real-time output streaming"""
    if env_key not in manager.environments:
        return False
    
    env = manager.environments[env_key]
    env_path = manager.base_path / "templates" / env["path"]
    
    if env.get("type") == "vagrant":
        # For Vagrant environments
        if not env_path.exists():
            socketio.emit('output', {'message': f'✅ Environment path does not exist, already cleared'})
            socketio.emit('terminal_output', {'output': f'✅ Environment path does not exist, already cleared\n'})
            return True  # If path doesn't exist, consider it cleared
        
        socketio.emit('output', {'message': f'🗺️ Destroying Vagrant environment... '})
        socketio.emit('terminal_output', {'output': f'🗺️ Destroying Vagrant environment...\n'})
        cmd = ["vagrant", "destroy", "-f"]
        return run_command_with_output(cmd, str(env_path))
    else:
        # Docker Compose environments
        socketio.emit('output', {'message': f'🐳 Clearing Docker Compose environment...\n'})
        socketio.emit('terminal_output', {'output': f'🐳 Clearing Docker Compose environment...\n'})
        cmd = ["docker-compose", "down"]
        if remove_volumes:
            cmd.append("--volumes")
        cmd.append("--remove-orphans")
        
        return run_command_with_output(cmd, str(env_path))

@socketio.on('delete_environment')
def handle_delete_environment(data):
    """Handle delete environment request"""
    env_key = data['env_key']
    remove_volumes = data.get('remove_volumes', False)
    remove_images = data.get('remove_images', False)
    
    emit('output', {'message': f'🗑️ Deleting {env_key} environment...'})
    
    def delete_worker():
        try:
            success = delete_environment_with_output(env_key, remove_volumes, remove_images)
            if success:
                socketio.emit('output', {'message': f'✅ Environment {env_key} deleted successfully!'})
                socketio.emit('refresh_environments')
            else:
                socketio.emit('output', {'message': f'❌ Failed to delete environment {env_key}'})
        except Exception as e:
            socketio.emit('output', {'message': f'❌ Delete error: {str(e)}'})
    
    thread = threading.Thread(target=delete_worker)
    thread.daemon = True
    thread.start()

def delete_environment_with_output(env_key: str, remove_volumes: bool = False, remove_images: bool = False):
    """Delete environment with real-time output streaming"""
    if env_key not in manager.environments:
        return False
    
    env = manager.environments[env_key]
    
    # First clear the environment (stop containers, remove volumes if requested)
    socketio.emit('output', {'message': f'🧹 Clearing {env_key} environment first...'}) 
    socketio.emit('terminal_output', {'output': f'🧹 Clearing {env_key} environment first...\n'}) 
    clear_environment_with_output(env_key, remove_volumes)
    
    # Remove images if requested
    if remove_images:
        socketio.emit('output', {'message': f'🗑️ Removing Docker image: {env["image"]}'}) 
        socketio.emit('terminal_output', {'output': f'🗑️ Removing Docker image: {env["image"]}\n'}) 
        cmd = ["docker", "rmi", "-f", env["image"]]
        run_command_with_output(cmd)
    
    # Remove template directory if it exists
    import shutil
    env_path = manager.base_path / "templates" / env["path"]
    if env_path.exists():
        try:
            socketio.emit('output', {'message': f'📁 Removing template directory: {env_path}'}) 
            socketio.emit('terminal_output', {'output': f'📁 Removing template directory: {env_path}\n'}) 
            shutil.rmtree(env_path)
            socketio.emit('output', {'message': f'✅ Template directory removed successfully'}) 
            socketio.emit('terminal_output', {'output': f'✅ Template directory removed successfully\n'}) 
        except Exception as e:
            socketio.emit('output', {'message': f'⚠️ Could not remove template directory: {str(e)}'}) 
            socketio.emit('terminal_output', {'output': f'⚠️ Could not remove template directory: {str(e)}\n'}) 
    
    # Remove from environments dictionary
    del manager.environments[env_key]
    manager.save_environments()
    socketio.emit('output', {'message': f'✅ Environment {env_key} removed from configuration'}) 
    socketio.emit('terminal_output', {'output': f'✅ Environment {env_key} removed from configuration\n'}) 
    
    return True

@app.route('/api/container-info/<env_key>')
def get_container_info(env_key):
    """Get container information"""
    if env_key not in manager.environments:
        return jsonify({'error': 'Environment not found'}), 404
    
    env = manager.environments[env_key]
    try:
        container_info = manager.get_container_info(env["container"])
        return jsonify(container_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/image-info/<env_key>')
def get_image_info(env_key):
    """Get image information"""
    if env_key not in manager.environments:
        return jsonify({'error': 'Environment not found'}), 404
    
    env = manager.environments[env_key]
    try:
        image_info = manager.get_image_info(env["image"])
        return jsonify(image_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clone-environment', methods=['POST'])
def clone_environment():
    """Clone an environment"""
    data = request.get_json()
    source_env = data.get('source_env')
    new_key = data.get('new_key')
    new_name = data.get('new_name')
    new_port = data.get('new_port')
    
    if not all([source_env, new_key, new_name, new_port]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        new_port = int(new_port)
        if new_port < 1 or new_port > 65535:
            return jsonify({'error': 'Port must be between 1 and 65535'}), 400
        
        if new_key in manager.environments:
            return jsonify({'error': f'Environment {new_key} already exists'}), 400
        
        # Check for port conflicts
        used_ports = [env["port"] for env in manager.environments.values()]
        if new_port in used_ports:
            return jsonify({'error': f'Port {new_port} is already in use'}), 400
        
        success = manager.clone_environment(source_env, new_key, new_name, new_port)
        if success:
            return jsonify({'message': f'Environment {new_key} cloned successfully'})
        else:
            return jsonify({'error': 'Failed to clone environment'}), 500
            
    except ValueError:
        return jsonify({'error': 'Invalid port number'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/edit-environment', methods=['POST'])
def edit_environment():
    """Edit an environment"""
    data = request.get_json()
    env_key = data.get('env_key')
    
    if env_key not in manager.environments:
        return jsonify({'error': 'Environment not found'}), 404
    
    try:
        env = manager.environments[env_key]
        
        # Update fields
        for field in ['name', 'path', 'port', 'container', 'image', 'volume']:
            if field in data:
                value = data[field]
                if field == 'port':
                    value = int(value)
                    if value < 1 or value > 65535:
                        return jsonify({'error': 'Port must be between 1 and 65535'}), 400
                    
                    # Check for port conflicts
                    for other_key, other_env in manager.environments.items():
                        if other_key != env_key and other_env["port"] == value:
                            return jsonify({'error': f'Port {value} is already used by {other_key}'}), 400
                
                env[field] = value
        
        manager.save_environments()
        return jsonify({'message': 'Environment updated successfully'})
        
    except ValueError:
        return jsonify({'error': 'Invalid port number'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/credentials/<env_key>', methods=['GET'])
def get_credentials(env_key):
    """Get stored credentials for an environment"""
    if env_key not in manager.environments:
        return jsonify({'error': 'Environment not found'}), 404
    
    credentials = container_credentials.get(env_key)
    if credentials:
        return jsonify({
            'username': credentials['username'],
            'password_length': len(credentials['password'])
        })
    else:
        return jsonify({'username': None, 'password_length': 0})

@app.route('/api/credentials/<env_key>', methods=['POST'])
def set_credentials(env_key):
    """Set credentials for an environment"""
    if env_key not in manager.environments:
        return jsonify({'error': 'Environment not found'}), 404
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Store credentials
    container_credentials[env_key] = {
        'username': username,
        'password': password
    }
    
    return jsonify({'message': 'Credentials saved successfully'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)