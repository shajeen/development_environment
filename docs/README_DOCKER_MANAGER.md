# Docker Development Environment Manager

A comprehensive solution for managing Docker-based development environments with a GUI.

## Features

- **Multiple Environment Support**: C++, CUDA, Python, and Python-CUDA environments

- **GUI Interface**: User-friendly graphical interface with `docker_manager_gui.py`
- **Complete Lifecycle Management**: Build, start, stop, restart, and clear environments
- **SSH Integration**: Direct SSH connection management
- **Real-time Status**: Live container status monitoring
- **Volume Management**: Optional volume removal for complete cleanup
- **Configuration Editing**: Edit all environment settings (name, port, paths, etc.)
- **Environment Cloning**: Clone existing environments with custom configurations
- **Persistent Configuration**: Settings saved to `docker_environments.json`


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

The GUI provides detailed output for:
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
- `name`: Display name shown in the GUI
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