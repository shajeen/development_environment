# Docker Development Environment Manager

A comprehensive solution for managing Docker-based development environments with both console and GUI interfaces.

## Features

- **Multiple Environment Support**: C++, CUDA, Python, and Python-CUDA environments
- **Console Interface**: Full command-line management with `docker_manager.py`
- **GUI Interface**: User-friendly graphical interface with `docker_manager_gui.py`
- **Complete Lifecycle Management**: Build, start, stop, restart, and clear environments
- **SSH Integration**: Direct SSH connection management
- **Real-time Status**: Live container status monitoring
- **Volume Management**: Optional volume removal for complete cleanup
- **Configuration Editing**: Edit all environment settings (name, port, paths, etc.)
- **Environment Cloning**: Clone existing environments with custom configurations
- **Persistent Configuration**: Settings saved to `docker_environments.json`
- **Interactive Editing**: Console-based interactive configuration editor

## Available Environments

| Environment | Description | Port | Container Name |
|-------------|-------------|------|----------------|
| `cpp` | C++ Development with GCC, CMake, GDB, Valgrind, Conan | 3001 | cpp.workspace.common |
| `cuda` | CUDA Development with NVIDIA toolkit | 3003 | cuda.workspace |
| `python` | Python 3.14 Development | 4001 | python.workspace.common |
| `python-cuda` | Python with CUDA support | 3004 | python.cuda.workspace |

## Installation

### Setup Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install PyYAML
```

### Required Dependencies

- `PyYAML` (YAML file handling for docker-compose.yaml updates)
- `tkinter` (GUI - usually included with Python)
- `subprocess` (command execution)
- `pathlib` (path handling)
- `json` (configuration storage)
- `shutil` (file operations for cloning)

## Usage

### Console Interface

```bash
# Make executable
chmod +x docker_manager.py

# List all environments
python docker_manager.py list

# Build an environment
python docker_manager.py build cpp
python docker_manager.py build cuda --no-cache

# Start an environment
python docker_manager.py start python

# Stop an environment
python docker_manager.py stop cpp

# Restart an environment
python docker_manager.py restart cuda

# Clear an environment
python docker_manager.py clear python
python docker_manager.py clear cuda --remove-volumes

# Get environment information
python docker_manager.py info cpp

# SSH into running environment
python docker_manager.py ssh python

# Edit environment configuration
python docker_manager.py edit cpp --field port --value 3005
python docker_manager.py edit python --field name --value "My Python Environment"

# Interactive editing
python docker_manager.py interactive-edit cuda

# Clone environment
python docker_manager.py clone my_cpp --source cpp --new-name "My Custom C++" --new-port 3010

# List editable fields
python docker_manager.py fields
```

### GUI Interface

```bash
# Launch GUI
python docker_manager_gui.py
```

**GUI Features:**
- Environment selection from list
- Real-time status indicators (🟢 running, 🔴 stopped, ⚪ not found)
- One-click build, start, stop, restart, clear operations
- SSH connection with terminal integration
- Build options (no-cache) and clear options (remove volumes)
- Live output display for all operations
- Environment information panel
- **✏️ Edit Button**: Edit all environment settings through dialog
- **📋 Clone Button**: Clone environments with custom configurations
- **Form Validation**: Input validation for ports, names, and paths
- **Auto-refresh**: Environment list updates after edits/clones

## Command Reference

### Console Commands

| Command | Description | Options |
|---------|-------------|---------|
| `list` | Show all environments with status | - |
| `build <env>` | Build environment | `--no-cache` |
| `start <env>` | Start environment | - |
| `stop <env>` | Stop environment | - |
| `restart <env>` | Restart environment | - |
| `clear <env>` | Clear environment | `--remove-volumes` |
| `info <env>` | Show environment details | - |
| `ssh <env>` | SSH into environment | - |
| `edit <env>` | Edit environment configuration | `--field <field> --value <value>` |
| `interactive-edit <env>` | Interactive editing session | - |
| `clone <new_env>` | Clone environment | `--source <env> --new-name <name> --new-port <port>` |
| `fields` | List all editable fields | - |

### Environment Keys

- `cpp` - C++ Development Environment
- `cuda` - CUDA Development Environment  
- `python` - Python Development Environment
- `python-cuda` - Python CUDA Workspace

## SSH Access

All environments use the same SSH credentials:
- **Username**: `dev`
- **Password**: `devpass`
- **Connection**: `ssh dev@localhost -p <port>`

## Examples

### Quick Start Workflow

```bash
# Activate virtual environment
source venv/bin/activate

# 1. List available environments
python docker_manager.py list

# 2. Build and start C++ environment
python docker_manager.py build cpp
python docker_manager.py start cpp

# 3. Connect via SSH
python docker_manager.py ssh cpp

# 4. When done, stop the environment
python docker_manager.py stop cpp
```

### Configuration Management Workflow

```bash
# Edit environment port
python docker_manager.py edit cpp --field port --value 3005

# Clone environment with custom settings
python docker_manager.py clone my_dev --source cpp --new-name "My Dev Environment" --new-port 3020

# Interactive editing session
python docker_manager.py interactive-edit my_dev

# List all editable fields
python docker_manager.py fields
```

### Development Workflow

```bash
# Build with fresh cache
python docker_manager.py build cuda --no-cache

# Start environment
python docker_manager.py start cuda

# Check status
python docker_manager.py info cuda

# Restart if needed
python docker_manager.py restart cuda

# Complete cleanup when done
python docker_manager.py clear cuda --remove-volumes
```

## GUI Workflow

1. **Launch GUI**: `source venv/bin/activate && python docker_manager_gui.py`
2. **Select Environment**: Click on desired environment in the list
3. **View Info**: Environment details appear in the information panel
4. **Build**: Click "🔨 Build" (optionally enable "No Cache")
5. **Start**: Click "🚀 Start" to run the environment
6. **SSH**: Click "🔌 SSH" to open terminal connection
7. **Stop**: Click "🛑 Stop" when finished
8. **Clear**: Click "🧹 Clear" for cleanup (optionally enable "Remove Volumes")
9. **Edit**: Click "✏️ Edit" to modify environment settings
10. **Clone**: Click "📋 Clone" to create a copy with custom configuration

### Edit Dialog Features

- **All Fields Editable**: Name, path, port, container name, image name, volume name
- **Input Validation**: Port range validation (1-65535)
- **Required Fields**: All fields must be filled
- **Live Updates**: Changes reflected immediately in environment list

### Clone Dialog Features

- **Source Information**: Shows details of environment being cloned
- **Custom Settings**: Set new key, name, and port
- **Port Conflict Detection**: Prevents duplicate port assignments
- **Auto-suggestions**: Suggests next available port
- **Directory Cloning**: Copies entire Docker configuration directory
- **docker-compose.yaml Updates**: Automatically updates configuration files

## Troubleshooting

### Common Issues

1. **Port conflicts**: Use edit feature to change ports or check for conflicts during cloning
2. **Permission errors**: Ensure Docker daemon is running and user has Docker permissions
3. **SSH connection fails**: Verify container is running and port is accessible
4. **Build failures**: Check Docker logs and ensure sufficient disk space
5. **PyYAML import error**: Ensure virtual environment is activated and PyYAML is installed
6. **Configuration not saved**: Check file permissions for `docker_environments.json`
7. **Clone directory exists**: Remove existing directory or choose different name
8. **GUI dialog not opening**: Ensure tkinter is installed and display is available

### Status Indicators

- **🟢 Running**: Container is active and accessible
- **🔴 Stopped**: Container exists but is not running
- **⚪ Not Found**: Container doesn't exist (needs to be built)

### Log Output

Both console and GUI provide detailed output for:
- Build progress and errors
- Container start/stop operations
- SSH connection status
- Error messages and warnings

## Configuration File

The manager uses `docker_environments.json` to store configuration:

```json
{
  "cpp": {
    "name": "C++ Development",
    "path": "docker/cpp",
    "port": 3001,
    "container": "cpp.workspace.common",
    "image": "cpp.workspace.image",
    "volume": "cpp.workspace.common.volume"
  }
}
```

**Editable Fields:**
- `name`: Display name shown in GUI and console
- `path`: Directory path containing Docker configuration
- `port`: SSH port for container access
- `container`: Docker container name
- `image`: Docker image name
- `volume`: Docker volume name

## Integration with Existing Project

The manager integrates with your existing Docker configurations:
- Uses existing `docker-compose.yaml` files
- Respects current port mappings
- Maintains existing volume configurations
- Works with current container naming conventions
- **Cloning**: Copies entire directory structure and updates configurations
- **Editing**: Updates both JSON config and docker-compose.yaml files
- **Validation**: Ensures no port conflicts or duplicate names

## Advanced Usage

### Custom Base Path

```bash
python docker_manager.py --path /custom/path list
```

### Automated Scripts

```bash
#!/bin/bash
# Auto-setup development environment
source venv/bin/activate

# Create custom environment
python docker_manager.py clone my_project --source cpp --new-name "My Project" --new-port 3100

# Build and start
python docker_manager.py build my_project --no-cache
python docker_manager.py start my_project

echo "Custom environment ready at: ssh dev@localhost -p 3100"
```

### Environment Customization

```bash
# Create specialized environments
python docker_manager.py clone gpu_ml --source cuda --new-name "GPU ML Environment" --new-port 3200
python docker_manager.py edit gpu_ml --field name --value "Machine Learning GPU Environment"

# Create team-specific environments
python docker_manager.py clone team_alpha --source python --new-name "Team Alpha Python" --new-port 4100
python docker_manager.py clone team_beta --source python --new-name "Team Beta Python" --new-port 4200
```

## File Structure After Cloning

```
development_environment/
├── docker_environments.json          # Environment configurations
├── docker_manager.py                 # Console application
├── docker_manager_gui.py            # GUI application  
├── gui_dialogs.py                   # Dialog classes
├── venv/                            # Virtual environment
├── docker/
│   ├── cpp/                         # Original C++ environment
│   ├── cuda/                        # Original CUDA environment
│   ├── python/                      # Original Python environment
│   └── my_cpp/                      # Cloned C++ environment
└── workspaces/
    └── python.cuda.template/
```

This manager provides a unified interface for your Docker development environments, making it easy to switch between different development contexts while maintaining consistent workflows. The editing and cloning features allow you to customize environments for specific projects or team needs without affecting the original configurations.