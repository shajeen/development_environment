#!/usr/bin/env python3
"""
Docker Development Environment Manager
A console application to manage Docker-based development environments
"""

import os
import sys
import subprocess
import json
import shutil
import re
from typing import Dict, List, Optional
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)

class DockerEnvironmentManager:
    """Manager for Docker development environments"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.config_file = self.base_path / "docker_environments.json"
        self.load_environments()
    
    def load_environments(self):
        """Load environments from config file or use defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.environments = json.load(f)
                return
            except Exception as e:
                logger.warning(f"Error loading config file {self.config_file}: {e}. Using default environments.")
        
        # Default environments - All discovered templates
        self.environments = {
            # Docker Compose environments
            "docker-cpp": {
                "name": "C++ Development (Docker)",
                "path": "docker/cpp",
                "port": 3001,
                "container": "cpp.workspace.common",
                "image": "cpp.workspace.image",
                "volume": "cpp.workspace.common.volume:/workspace",
                "type": "docker-compose",
                "base_image": "gcc:latest",
                "description": "C++ development with GCC, CMake, Git, GDB, Clang, LLVM, Valgrind, Conan package manager, Google Test"
            },
            "docker-cuda": {
                "name": "CUDA Development (Docker)", 
                "path": "docker/cuda",
                "port": 3003,
                "container": "cuda.workspace",
                "image": "cuda.workspace.image",
                "volume": "cuda_workspace_volume:/workspace",
                "type": "docker-compose",
                "base_image": "nvidia/cuda:12.9.0-cudnn-devel-ubuntu24.04",
                "description": "NVIDIA CUDA 12.9.0 with CUDNN development environment, CMake, GDB, Clang, LLVM, Valgrind",
                "gpu_support": True
            },
            "docker-python": {
                "name": "Python Development (Docker)",
                "path": "docker/python", 
                "port": 4001,
                "container": "python.workspace.common",
                "image": "python.workspace.image",
                "volume": "python.workspace.common.volume:/workspace",
                "type": "docker-compose",
                "base_image": "python:3.14.0b1-slim-bookworm",
                "description": "Python 3.14 development environment with essential packages and debugging support"
            },
            "docker-python-cuda": {
                "name": "Python CUDA Workspace (Docker)",
                "path": "workspaces/python.cuda.template",
                "port": 3004,
                "container": "python.cuda.workspace", 
                "image": "python.cuda.workspace.image",
                "volume": "python_cuda_workspace_volume:/workspace",
                "type": "docker-compose",
                "base_image": "nvidia/cuda:12.9.0-cudnn-devel-ubuntu24.04",
                "description": "Python + CUDA development with web interface support",
                "gpu_support": True,
                "web_port": 7860
            },
            # Vagrant environments
            "vagrant-ubuntu": {
                "name": "Ubuntu Core VM (Vagrant)",
                "path": "vagrant/ubuntu",
                "port": 1000,
                "container": "docker-ubuntu-core",
                "image": "ubuntu-core",
                "volume": "workspace:/workspace",
                "type": "vagrant",
                "ssh_user": "dev",
                "description": "Basic Ubuntu development environment with cross-platform volume mounting"
            },
            "vagrant-ubuntu-cuda": {
                "name": "Ubuntu CUDA VM (Vagrant)",
                "path": "vagrant/ubuntu_cuda",
                "port": 2000,
                "container": "docker-ubuntu-cuda",
                "image": "ubuntu-cuda",
                "volume": "workspace:/workspace",
                "type": "vagrant",
                "ssh_user": "dev",
                "description": "Ubuntu with NVIDIA GPU support for CUDA development",
                "gpu_support": True
            },
            "vagrant-ubuntu-cuda-vnc": {
                "name": "Ubuntu CUDA VNC VM (Vagrant)",
                "path": "vagrant/ubuntu_cuda_vnc",
                "port": 3000,
                "container": "docker-ubuntu-cuda-vnc",
                "image": "ubuntu-cuda-vnc",
                "volume": "workspace:/workspace",
                "type": "vagrant",
                "ssh_user": "dev",
                "vnc_port": 6000,
                "description": "Ubuntu with NVIDIA GPU support and VNC remote desktop access",
                "gpu_support": True
            },
            "vagrant-cpp": {
                "name": "C++ Development VM (Vagrant)",
                "path": "vagrant/cpp",
                "port": 1002,
                "container": "docker-cpp",
                "image": "cpp_core_latest",
                "volume": "workspace:/workspace",
                "type": "vagrant",
                "ssh_user": "dev",
                "description": "C++ development environment with build tools and cross-platform support"
            },
            "vagrant-python": {
                "name": "Python Development VM (Vagrant)",
                "path": "vagrant/python",
                "port": 1001,
                "container": "docker-python-core",
                "image": "python-core-latest",
                "volume": "workspace:/workspace",
                "type": "vagrant",
                "ssh_user": "dev",
                "description": "Python development environment with essential packages and cross-platform support"
            }
        }
        self.save_environments()
    
    def save_environments(self):
        """Save environments to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.environments, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config file {self.config_file}: {e}")
    
    def run_command(self, command: List[str], cwd: str = None) -> tuple:
        """Run a shell command and return output"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=cwd or self.base_path,
                check=False
            )
            if result.returncode != 0:
                logger.error(f"Command failed: {' '.join(command)}\nStdout: {result.stdout}\nStderr: {result.stderr}")
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            logger.exception(f"Exception while running command: {' '.join(command)}")
            return 1, "", str(e)
    
    def get_environments_list(self) -> list:
        """Get all available environments with their status"""
        environments = []
        for key, env in self.environments.items():
            env_type = env.get("type", "docker-compose")
            env_path = self.base_path / "templates" / env["path"] if env_type == "vagrant" else None
            status = self.get_container_status(env["container"], env_type, str(env_path) if env_path else None)
            environments.append({
                "key": key,
                "name": env["name"],
                "type": env_type,
                "status": status,
                "port": env["port"],
                "config": env
            })
        return environments
    
    def get_container_status(self, container_name: str, env_type: str = "docker-compose", env_path: str = None) -> str:
        """Get the comprehensive status of a container or Vagrant environment"""
        if env_type == "vagrant" and env_path:
            # Check if vagrant path exists
            if not os.path.exists(env_path):
                return "path not found"
            return self.get_vagrant_status(env_path)
        else:
            # Docker container - check comprehensive status
            return self.get_docker_environment_status(container_name)
    
    def get_docker_environment_status(self, container_name: str) -> str:
        """Get comprehensive Docker environment status"""
        try:
            # First check if container exists and its status
            returncode, stdout, _ = self.run_command([
                "docker", "inspect", "--format={{.State.Status}}", container_name
            ])
            
            if returncode == 0:
                # Container exists, return its status
                return stdout.strip()
            
            # Container doesn't exist, check if image is built
            # Try to find environment by container name
            image_name = None
            env_path_for_template = None
            for env_key, env in self.environments.items():
                if env["container"] == container_name:
                    image_name = env["image"]
                    env_path_for_template = env["path"]
                    break
            
            if not image_name:
                return "not found"
            
            # Check if image exists
            returncode, stdout, _ = self.run_command([
                "docker", "images", "--format", "{{.Repository}}:{{.Tag}}", image_name
            ])
            
            if returncode == 0 and stdout.strip():
                return "built"
            
            # Image doesn't exist, check if template directory exists
            if env_path_for_template:
                template_path = self.base_path / "templates" / env_path_for_template
                if template_path.exists():
                    return "template-ready"
            
            return "not found"
            
        except Exception as e:
            return "error"
    
    def get_container_info(self, container_name: str) -> dict:
        """Get detailed container information"""
        info = {
            "exists": False,
            "status": "not found",
            "image": "N/A",
            "created": "N/A",
            "ports": "N/A"
        }
        
        # Check if container exists
        returncode, stdout, _ = self.run_command([
            "docker", "inspect", container_name
        ])
        
        if returncode == 0:
            info["exists"] = True
            
            # Get status
            returncode, stdout, _ = self.run_command([
                "docker", "inspect", "--format={{.State.Status}}", container_name
            ])
            if returncode == 0:
                info["status"] = stdout.strip()
            
            # Get image
            returncode, stdout, _ = self.run_command([
                "docker", "inspect", "--format={{.Config.Image}}", container_name
            ])
            if returncode == 0:
                info["image"] = stdout.strip()
            
            # Get created time
            returncode, stdout, _ = self.run_command([
                "docker", "inspect", "--format={{.Created}}", container_name
            ])
            if returncode == 0:
                info["created"] = stdout.strip()[:19]  # Get first 19 chars (date part)
            
            # Get ports
            returncode, stdout, _ = self.run_command([
                "docker", "port", container_name
            ])
            if returncode == 0:
                info["ports"] = stdout.strip() or "No ports mapped"
        
        return info
    
    def get_image_info(self, image_name: str) -> dict:
        """Get detailed image information"""
        info = {
            "exists": False,
            "size": "N/A",
            "created": "N/A",
            "id": "N/A"
        }
        
        # Check if image exists
        returncode, stdout, _ = self.run_command([
            "docker", "images", "--format", "{{.Repository}}:{{.Tag}}", image_name
        ])
        
        if returncode == 0 and stdout.strip():
            info["exists"] = True
            
            # Get size
            returncode, stdout, _ = self.run_command([
                "docker", "images", "--format", "{{.Size}}", image_name
            ])
            if returncode == 0:
                info["size"] = stdout.strip()
            
            # Get created time
            returncode, stdout, _ = self.run_command([
                "docker", "images", "--format", "{{.CreatedAt}}", image_name
            ])
            if returncode == 0:
                info["created"] = stdout.strip()[:19]  # Get first 19 chars (date part)
            
            # Get image ID
            returncode, stdout, _ = self.run_command([
                "docker", "images", "--format", "{{.ID}}", image_name
            ])
            if returncode == 0:
                info["id"] = stdout.strip()
        
        return info
    
    def delete_environment(self, env_key: str, remove_volumes: bool = False, remove_images: bool = False) -> bool:
        """Delete an environment completely"""
        if env_key not in self.environments:
            return False
        
        env = self.environments[env_key]
        
        # First clear the environment (stop containers, remove volumes if requested)
        self.clear_environment(env_key, remove_volumes)
        
        # Remove images if requested
        if remove_images:
            returncode, stdout, stderr = self.run_command([
                "docker", "rmi", "-f", env["image"]
            ])
        
        # Remove template directory if it exists
        env_path = self.base_path / "templates" / env["path"]
        if env_path.exists():
            try:
                shutil.rmtree(env_path)
            except Exception as e:
                logger.error(f"Could not remove template directory {env_path}: {e}")
        
        # Remove from environments dictionary
        del self.environments[env_key]
        self.save_environments()
        
        return True
    
    def get_vagrant_status(self, env_path: str) -> str:
        """Get the status of a Vagrant environment"""
        try:
            # First try simple vagrant status
            returncode, stdout, stderr = self.run_command([
                "vagrant", "status"
            ], cwd=str(env_path))
            
            if returncode == 0:
                # Parse simple output - look for running/stopped indicators
                if "running" in stdout.lower():
                    return "running"
                elif "stopped" in stdout.lower() or "poweroff" in stdout.lower():
                    return "stopped"
                elif "not created" in stdout.lower():
                    return "not created"
                else:
                    return "unknown"
            else:
                # If vagrant command fails, try machine-readable format
                returncode, stdout, stderr = self.run_command([
                    "vagrant", "status", "--machine-readable"
                ], cwd=str(env_path))
                
                if returncode == 0:
                    # Parse machine-readable output
                    for line in stdout.split('\n'):
                        if ',state,' in line:
                            parts = line.split(',')
                            if len(parts) > 3:
                                state = parts[3]
                                if state == "running":
                                    return "running"
                                elif state in ["stopped", "poweroff", "aborted"]:
                                    return "stopped"
                                else:
                                    return state
                return "not found"
        except Exception as e:
            return "error"
    
    def build_environment(self, env_key: str, no_cache: bool = False) -> bool:
        """Build a Docker or Vagrant environment"""
        if env_key not in self.environments:
            return False
        
        env = self.environments[env_key]
        env_path = self.base_path / "templates" / env["path"]
        
        if not env_path.exists():
            return False
        
        if env.get("type") == "vagrant":
            # For Vagrant environments, build the Docker image first
            if not env_path.exists():
                return False
            
            dockerfile_path = env_path / "Dockerfile"
            if dockerfile_path.exists():
                cmd = ["docker", "build", "-t", env["image"], "."]
                if no_cache:
                    cmd.append("--no-cache")
                
                returncode, stdout, stderr = self.run_command(cmd, cwd=str(env_path))
                return returncode == 0
            else:
                # No Dockerfile found, but that's OK for some Vagrant environments
                return True
        else:
            # Docker Compose environments
            cmd = ["docker-compose", "build"]
            if no_cache:
                cmd.append("--no-cache")
            
            returncode, stdout, stderr = self.run_command(cmd, cwd=str(env_path))
            
            return returncode == 0
    
    def start_environment(self, env_key: str) -> bool:
        """Start a Docker or Vagrant environment"""
        if env_key not in self.environments:
            return False
        
        env = self.environments[env_key]
        env_path = self.base_path / "templates" / env["path"]
        
        if env.get("type") == "vagrant":
            # For Vagrant environments
            if not env_path.exists():
                return False
            
            # Check if Vagrantfile exists
            vagrantfile_path = env_path / "Vagrantfile"
            if not vagrantfile_path.exists():
                return False
            
            returncode, stdout, stderr = self.run_command([
                "vagrant", "up"
            ], cwd=str(env_path))
            
            return returncode == 0
        else:
            # Docker Compose environments
            returncode, stdout, stderr = self.run_command([
                "docker-compose", "up", "-d"
            ], cwd=str(env_path))
            
            return returncode == 0
    
    def stop_environment(self, env_key: str) -> bool:
        """Stop a Docker or Vagrant environment"""
        if env_key not in self.environments:
            return False
        
        env = self.environments[env_key]
        env_path = self.base_path / "templates" / env["path"]
        
        if env.get("type") == "vagrant":
            # For Vagrant environments
            if not env_path.exists():
                return False
            
            returncode, stdout, stderr = self.run_command([
                "vagrant", "halt"
            ], cwd=str(env_path))
            
            return returncode == 0
        else:
            # Docker Compose environments
            returncode, stdout, stderr = self.run_command([
                "docker-compose", "down"
            ], cwd=str(env_path))
            
            return returncode == 0
    
    def clear_environment(self, env_key: str, remove_volumes: bool = False) -> bool:
        """Clear/remove a Docker or Vagrant environment"""
        if env_key not in self.environments:
            return False
        
        env = self.environments[env_key]
        env_path = self.base_path / "templates" / env["path"]
        
        if env.get("type") == "vagrant":
            # For Vagrant environments
            if not env_path.exists():
                return True  # If path doesn't exist, consider it cleared
            
            returncode, stdout, stderr = self.run_command([
                "vagrant", "destroy", "-f"
            ], cwd=str(env_path))
            
            # Remove the Docker image
            returncode, stdout, stderr = self.run_command([
                "docker", "rmi", env["image"]
            ])
            if returncode != 0:
                logger.error(f"Failed to remove Docker image {env["image"]}: {stderr}")
            
            return True
        else:
            # Docker Compose environments
            # Stop and remove containers
            cmd = ["docker-compose", "down"]
            if remove_volumes:
                cmd.append("--volumes")
            
            returncode, stdout, stderr = self.run_command(cmd, cwd=str(env_path))
            if returncode != 0:
                logger.error(f"Failed to stop and remove Docker Compose environment at {env_path}: {stderr}")
            
            # Remove images
            returncode, stdout, stderr = self.run_command([
                "docker", "rmi", env["image"]
            ])
            if returncode != 0:
                logger.error(f"Failed to remove Docker image {env["image"]}: {stderr}")
            
            return True
    
    def restart_environment(self, env_key: str) -> bool:
        """Restart a Docker environment"""
        # Restart environment - GUI handles output
        return self.stop_environment(env_key) and self.start_environment(env_key)
    
    # Console-specific methods removed - get_environment_info and ssh_connect
    # These functions are handled by the GUI directly
    
    def edit_environment(self, env_key: str, field: str, value: str) -> bool:
        """Edit a specific field of an environment"""
        if env_key not in self.environments:
            return False
        
        valid_fields = ["name", "path", "port", "container", "image", "volume"]
        if field not in valid_fields:
            return False
        
        old_value = self.environments[env_key][field]
        
        # Type conversion and validation for port
        if field == "port":
            try:
                value = int(value)
                if value < 1 or value > 65535:
                    return False
                
                # Check for port conflicts with other environments
                for other_key, other_env in self.environments.items():
                    if other_key != env_key and other_env["port"] == value:
                        return False
            except ValueError:
                return False
        
        # Path validation - GUI will handle path validation
        if field == "path":
            path_obj = self.base_path / value
            if not path_obj.exists():
                return False
        
        self.environments[env_key][field] = value
        self.save_environments()
        
        # Update completed successfully - GUI handles success messages
        return True
    
    def clone_environment(self, source_env: str, new_env: str, new_name: str = None, new_port: int = None) -> bool:
        """Clone an existing environment"""
        if source_env not in self.environments:
            return False
        
        if new_env in self.environments:
            return False
        
        # Clone the environment configuration
        source_config = self.environments[source_env].copy()
        
        # Update with new values
        source_config["name"] = new_name or f"{source_config['name']} (Clone)"
        
        # Handle port assignment
        if new_port:
            source_config["port"] = new_port
        else:
            # Auto-assign next available port
            used_ports = [env["port"] for env in self.environments.values()]
            source_config["port"] = max(used_ports) + 1
        
        # Handle environment type-specific configuration
        env_type = source_config.get("type", "docker-compose")
        
        if env_type == "vagrant":
            # For Vagrant environments
            source_config["container"] = f"docker-{new_env}"
            source_config["image"] = f"{new_env}-image"
            source_config["volume"] = "workspace:/workspace"
        else:
            # For Docker Compose environments
            source_config["container"] = f"{new_env}.workspace"
            source_config["image"] = f"{new_env}.workspace.image"
            source_config["volume"] = f"{new_env}_workspace_volume:/workspace"
        
        # Create new path - fix the path calculation
        source_path = Path(source_config["path"])
        new_path = source_path.parent / new_env
        source_config["path"] = str(new_path)
        
        # Clone the directory structure
        source_full_path = self.base_path / "templates" / self.environments[source_env]["path"]
        new_full_path = self.base_path / "templates" / new_path
        
        try:
            if source_full_path.exists():
                # Remove destination if it exists
                if new_full_path.exists():
                    shutil.rmtree(new_full_path)
                
                # Copy the directory
                shutil.copytree(source_full_path, new_full_path)
                
                # Update configuration files based on environment type
                if env_type == "docker-compose":
                    self.update_docker_compose(new_full_path, source_config)
                elif env_type == "vagrant":
                    self.update_vagrantfile(new_full_path, source_config)
            else:
                # If source directory doesn't exist, still create the configuration
                # This allows cloning of environments that don't have physical directories
                pass
        except Exception as e:
            return False
        
        # Add to environments
        self.environments[new_env] = source_config
        self.save_environments()
        
        return True
    
    def update_docker_compose(self, env_path: Path, config: dict):
        """Update docker-compose.yaml with new configuration"""
        compose_file = env_path / "docker-compose.yaml"
        if not compose_file.exists():
            return
        
        try:
            with open(compose_file, 'r') as f:
                compose_data = yaml.safe_load(f)
            
            # Update service configuration
            service_name = list(compose_data['services'].keys())[0]
            service = compose_data['services'][service_name]
            
            # Update container name, image, and ports
            service['container_name'] = config['container']
            service['image'] = config['image']
            service['ports'] = [f"{config['port']}:22"]
            
            # Update dockerfile path
            if 'build' in service and 'dockerfile' in service['build']:
                service['build']['dockerfile'] = config['path'] + '/Dockerfile'
            
            # Update volumes
            if 'volumes' in service:
                volume_name = config['volume'].split(':')[0]  # Get volume name before colon
                service['volumes'] = [config['volume']]  # Use full volume specification
                
                # Update volume definition
                if 'volumes' in compose_data:
                    compose_data['volumes'] = {volume_name: {}}
            
            # Write updated compose file
            with open(compose_file, 'w') as f:
                yaml.dump(compose_data, f, default_flow_style=False)
                
        except Exception as e:
            logger.error(f"Error updating docker-compose.yaml at {compose_file}: {e}")
    
    def update_vagrantfile(self, env_path: Path, config: dict):
        """Update Vagrantfile with new configuration"""
        vagrantfile = env_path / "Vagrantfile"
        if not vagrantfile.exists():
            return
        
        try:
            with open(vagrantfile, 'r') as f:
                content = f.read()
            
            # Update the configuration in the Vagrantfile
            # This is a comprehensive text replacement approach
            
            # Extract the container name for vm.define
            container_name = config["container"]
            vm_define_name = container_name
            
            # Update vm.define name (more robust pattern)
            old_define_pattern = r'config\\.vm\\.define\\s+"[^"]*"'
            new_define = f'config.vm.define "{vm_define_name}"'
            content = re.sub(old_define_pattern, new_define, content)
            
            # Update image name
            old_image_pattern = r'd\\.image\\s*=\\s*"[^"]*"'
            new_image = f'd.image = "{config["image"]}"'
            content = re.sub(old_image_pattern, new_image, content)
            
            # Update ports - more flexible pattern
            old_port_pattern = r'd\\.ports\\s*=\\s*\["[^"]*"\]'
            new_ports = f'd.ports = ["{config["port"]}:22"]'
            content = re.sub(old_port_pattern, new_ports, content)
            
            # Update SSH port
            old_ssh_port_pattern = r'ssh\\.port\\s*=\\s*\\d+'
            new_ssh_port = f'ssh.port = {config["port"]}'
            content = re.sub(old_ssh_port_pattern, new_ssh_port, content)
            
            # Update port in comments if they exist
            old_comment_pattern = r'# Only map port 22 to \\d+'
            new_comment = f'# Only map port 22 to {config["port"]}'
            content = re.sub(old_comment_pattern, new_comment, content)
            
            # Update connection port in comments
            old_connect_comment_pattern = r'# Connect using port \\d+'
            new_connect_comment = f'# Connect using port {config["port"]}'
            content = re.sub(old_connect_comment_pattern, new_connect_comment, content)
            
            # Write updated Vagrantfile
            with open(vagrantfile, 'w') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"Error updating Vagrantfile at {vagrantfile}: {e}")
    
    