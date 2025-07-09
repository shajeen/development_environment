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


from src.core.docker_manager import DockerEnvironmentManager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-env-ops-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Global manager instance
manager = DockerEnvironmentManager()

# Status cache for performance
status_cache = {}
last_status_check = 0

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
        # TODO: Implement secure handling of credentials
        env_info['credentials'] = "Credentials not available via web interface"
    
    return jsonify(env_info)

@socketio.on('build_environment')
def handle_build_environment(data):
    """Handle build environment request"""
    env_key = data['env_key']
    no_cache = data.get('no_cache', False)
    
    logger.info(f"Received build_environment request for {env_key}, no_cache={no_cache}")
    emit('output', {'message': f'Building {env_key} environment...'})
    
    def build_worker():
        try:
            logger.info(f"Starting build for {env_key}")
            success = build_environment_with_output(env_key, no_cache)
            status = "✅ Build completed successfully!" if success else "❌ Build failed!"
            logger.info(f"Build completed for {env_key}, success={success}")
            socketio.emit('output', {'message': status})
            socketio.emit('refresh_status')
        except Exception as e:
            logger.exception(f"Build error for {env_key}")
            socketio.emit('output', {'message': f'❌ Build error: {str(e)}'})
    
    thread = threading.Thread(target=build_worker)
    thread.daemon = True
    thread.start()

def build_environment_with_output(env_key: str, no_cache: bool = False):
    """Build environment with real-time output streaming"""
    logger.debug(f"build_environment_with_output called for {env_key}")
    if env_key not in manager.environments:
        logger.debug(f"Environment {env_key} not found in manager.environments")
        return False
    
    env = manager.environments[env_key]
    env_path = manager.base_path / "templates" / env["path"]
    logger.debug(f"Environment path: {env_path}")
    
    if not env_path.exists():
        logger.debug(f"Environment path does not exist: {env_path}")
        socketio.emit('output', {'message': f'❌ Environment path does not exist: {env_path}'})
        return False
    
    if env.get("type") == "vagrant":
        logger.debug(f"Building Vagrant environment")
        socketio.emit('output', {'message': f'🗺️ Building Vagrant environment...'})
        
        # For Vagrant environments, build the Docker image first
        dockerfile_path = env_path / "Dockerfile"
        if dockerfile_path.exists():
            socketio.emit('output', {'message': f'🐳 Building Docker image: {env["image"]}'})
            cmd = ["docker", "build", "-t", env["image"], "."]
            if no_cache:
                cmd.append("--no-cache")
            
            return run_command_with_output(cmd, str(env_path))
        else:
            # No Dockerfile found, but that's OK for some Vagrant environments
            socketio.emit('output', {'message': f'✅ No Dockerfile found, Vagrant environment ready'})
            return True
    else:
        logger.debug(f"Building Docker Compose environment")
        # Docker Compose environments
        cmd = ["docker-compose", "build"]
        if no_cache:
            cmd.append("--no-cache")
        
        return run_command_with_output(cmd, str(env_path))

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
        logger.debug(f"About to run command: {' '.join(cmd)} in {cwd}")
        socketio.emit('output', {'message': f'🔧 Running: {" ".join(cmd)}'})
        logger.debug(f"Emitted initial message")
        
        # Set environment variables to disable buffering
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        env['DOCKER_BUILDKIT'] = '0'  # Disable BuildKit for more verbose output
        env['COMPOSE_DOCKER_CLI_BUILD'] = '0'  # Use classic docker build
        
        # Vagrant-specific environment variables
        if cmd and cmd[0] == 'vagrant':
            env['VAGRANT_NO_COLOR'] = '1'  # Disable color output for cleaner logs
            env['VAGRANT_LOG'] = 'info'  # Set log level to info
        
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
        logger.debug(f"Process started with PID: {process.pid}")
        
        # Read output line by line in real-time
        while True:
            line = process.stdout.readline()
            if line:
                logger.debug(f"OUTPUT: {line.rstrip()}")
                try:
                    # Add better formatting for Vagrant output
                    if cmd and cmd[0] == 'vagrant':
                        # Format Vagrant-specific output
                        formatted_line = format_vagrant_output(line.rstrip())
                        socketio.emit('output', {'message': formatted_line})
                    else:
                        socketio.emit('output', {'message': f'📤 {line.rstrip()}'})
                except Exception as emit_error:
                    logger.exception(f"Emit error")
            elif process.poll() is not None:
                logger.debug(f"Process finished")
                break
        
        returncode = process.returncode
        logger.debug(f"Exit code: {returncode}")
        try:
            socketio.emit('output', {'message': f'✅ Command completed with exit code: {returncode}'})
        except Exception as emit_error:
            logger.exception(f"Final emit error")
        return returncode == 0
        
    except Exception as e:
        logger.exception(f"Command error")
        socketio.emit('output', {'message': f'❌ Command error: {str(e)}'})
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
                    # TODO: Implement secure handling of credentials
                    socketio.emit('output', {'message': f'🔑 Credentials: Not available via web interface'}))
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
    if env_key not in manager.environments:
        return False
    
    env = manager.environments[env_key]
    env_path = manager.base_path / "templates" / env["path"]
    
    if env.get("type") == "vagrant":
        # For Vagrant environments
        if not env_path.exists():
            socketio.emit('output', {'message': f'❌ Environment path does not exist: {env_path}'})
            return False
        
        socketio.emit('output', {'message': f'🗺️ Starting Vagrant environment...'})
        cmd = ["vagrant", "up", "--provider=virtualbox"]
        return run_command_with_output(cmd, str(env_path))
    else:
        # Docker Compose environments
        cmd = ["docker-compose", "up", "-d"]
        return run_command_with_output(cmd, str(env_path))

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
        cmd = ["vagrant", "halt"]
        return run_command_with_output(cmd, str(env_path))
    else:
        # Docker Compose environments
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
                    # TODO: Implement secure handling of credentials
                    socketio.emit('output', {'message': f'🔑 Credentials: Not available via web interface'}))
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
            return True  # If path doesn't exist, consider it cleared
        
        socketio.emit('output', {'message': f'🗺️ Destroying Vagrant environment...'})
        cmd = ["vagrant", "destroy", "-f"]
        return run_command_with_output(cmd, str(env_path))
    else:
        # Docker Compose environments
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
    clear_environment_with_output(env_key, remove_volumes)
    
    # Remove images if requested
    if remove_images:
        socketio.emit('output', {'message': f'🗑️ Removing Docker image: {env["image"]}'})
        cmd = ["docker", "rmi", "-f", env["image"]]
        run_command_with_output(cmd)
    
    # Remove template directory if it exists
    import shutil
    env_path = manager.base_path / "templates" / env["path"]
    if env_path.exists():
        try:
            socketio.emit('output', {'message': f'📁 Removing template directory: {env_path}'})
            shutil.rmtree(env_path)
            socketio.emit('output', {'message': f'✅ Template directory removed successfully'})
        except Exception as e:
            socketio.emit('output', {'message': f'⚠️ Could not remove template directory: {str(e)}'})
    
    # Remove from environments dictionary
    del manager.environments[env_key]
    manager.save_environments()
    socketio.emit('output', {'message': f'✅ Environment {env_key} removed from configuration'})
    
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

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)