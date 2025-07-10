# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DevEnvOps is a Development Environment Orchestrator that manages Docker and Vagrant development environments through a unified GUI interface. It provides pre-configured templates for C++, CUDA, and Python development environments with environment cloning and customization capabilities.

## Core Architecture

### Key Components

- **DockerEnvironmentManager** (`src/core/docker_manager.py`): Core logic for managing Docker environments, loading configurations, and orchestrating Docker operations
- **Web Application** (`src/web/app.py`): Flask-based web interface with WebSocket support for real-time environment management
- **DockerManagerGUI** (`src/gui/docker_manager_gui.py`): Legacy tkinter GUI application for environment management
- **GUI Dialogs** (`src/gui/gui_dialogs.py`, `src/gui/container_image_info_dialog.py`): Dialog components for editing environments and viewing container information
- **Configuration**: Environment definitions stored in `docker_environments.json` with fallback defaults in the manager

### Project Structure

```
src/
├── core/
│   └── docker_manager.py          # Main environment management logic
├── web/
│   ├── app.py                     # Flask web application
│   └── templates/
│       ├── base.html              # Base template
│       └── index.html             # Main web interface
├── gui/
│   ├── docker_manager_gui.py      # Legacy tkinter GUI application
│   ├── gui_dialogs.py             # Environment editing dialogs
│   └── container_image_info_dialog.py  # Container information display
└── config/
    └── docker_environments.json   # Environment configuration backup
```

### Environment Templates

The application manages two types of environments:

1. **Docker Compose Environments**: Located in `templates/docker/` with Dockerfile and docker-compose.yaml
2. **Vagrant Environments**: Located in `templates/vagrant/` with Vagrantfile and Docker build scripts

Available templates include:
- C++ Development (GCC, CMake, Git, GDB, Clang, LLVM, Valgrind, Conan, Google Test)
- CUDA Development (NVIDIA CUDA, CUDNN, GPU programming tools)
- Python Development (Python 3.14, build tools, SSH access)

## Common Development Commands

### Running the Application

```bash
# Activate virtual environment (required before running)
source venv/bin/activate

# Start the web application (default - recommended)
./start_web.py

# Alternative: Start the GUI application (legacy)
./start_gui.py

# Direct web application method
python3 src/web/app.py

# Alternative direct GUI method
python3 src/gui/docker_manager_gui.py
```

### Web Application Access

The web application runs on `http://localhost:5000` by default. It provides:
- Real-time environment status updates via WebSockets
- Interactive environment management interface
- Container and image information dialogs
- Environment cloning and editing capabilities

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize virtual environment (if needed)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Dependencies

- **PyYAML>=6.0.0**: YAML configuration parsing
- **Flask>=2.3.0**: Web framework for the web application
- **Flask-SocketIO>=5.3.0**: WebSocket support for real-time updates
- **eventlet>=0.33.0**: WSGI server for SocketIO support

### Testing

```bash
# Run the GUI test script (validates paths and environment loading)
python3 tests/test_gui.py

# The test script verifies:
# - Manager initialization
# - Environment configuration loading
# - Template path validation
```

## Key Configuration Files

- `docker_environments.json`: Main environment configuration with paths, ports, container names, and descriptions
- `requirements.txt`: Python dependencies (currently only PyYAML>=6.0.0)
- `start_gui.py`: Entry point script that sets PYTHONPATH and launches the GUI

## Environment Management Flow

1. **Environment Loading**: `DockerEnvironmentManager` loads from `docker_environments.json` or uses hardcoded defaults
2. **GUI Initialization**: `DockerManagerGUI` creates the interface with environment list and controls
3. **Operations**: Start/stop/build environments through Docker Compose or Vagrant commands
4. **Cloning**: Users can clone existing environments to create customized versions
5. **Status Monitoring**: Real-time status updates for running containers and environments

## Container Credential Management System

The application implements a secure credential management system for container access:

### Credential Workflow
1. **Build Trigger**: When users click "Build" for Docker environments, a credentials modal appears
2. **User Input**: Modal collects username (default: "dev") and custom password
3. **Server Storage**: Credentials stored in-memory via `/api/credentials/<env_key>` endpoints
4. **Build Integration**: `DEV_PASSWORD` build argument passed to Docker during build process
5. **Password Setting**: Dockerfile uses `ARG DEV_PASSWORD` and `echo "dev:${DEV_PASSWORD}" | chpasswd`

### Key Files for Credential System
- **Frontend Modal**: `src/web/templates/index.html` (lines 251-284)
- **JavaScript Functions**: `showCredentialsForBuild()`, `proceedWithBuild()`, `togglePasswordVisibility()`
- **Backend API**: `src/web/app.py` - GET/POST `/api/credentials/<env_key>` (lines 700-734)
- **Build Integration**: `run_command_with_output_and_credentials()` function
- **Docker Templates**: All Dockerfiles accept `ARG DEV_PASSWORD=devpass`

### Security Features
- In-memory credential storage (cleared on restart)
- Password masking in UI display
- Environment-specific credentials (not global)
- Fallback to default "devpass" if no custom credentials set
- Credentials only prompted for Docker environments, not Vagrant

## Architecture Deep Dive

### Web Application Architecture
- **Flask + SocketIO**: Real-time WebSocket communication for build/operation status
- **Threading**: Non-blocking operations using `threading.Thread` for long-running commands
- **Caching**: Status cache with 5-second TTL to reduce Docker API calls
- **Error Handling**: Graceful handling of "No such object" Docker errors (logged as debug, not error)

### Environment Configuration System
- **JSON Configuration**: `docker_environments.json` stores environment definitions
- **Fallback Defaults**: Hardcoded defaults in `DockerEnvironmentManager.__init__()` if config missing
- **Dynamic Loading**: Environments loaded/reloaded via `load_environments()` method
- **Cloning Logic**: `clone_environment()` creates new template directories with modified configs

### Docker vs Vagrant Distinction
- **Docker Environments**: Use docker-compose with build args for credentials
- **Vagrant Environments**: Use Vagrantfile with SSH key authentication
- **Path Structure**: `templates/docker/` vs `templates/vagrant/` for respective types
- **Build Process**: Different command execution paths based on environment type

## Important Implementation Details

- **Command Execution**: All Docker/Vagrant commands run through `run_command()` with proper error handling
- **Environment Status**: Comprehensive status checking via `get_container_status()` and `get_vagrant_status()`
- **Real-time Updates**: WebSocket events (`refresh_status`, `refresh_environments`) for UI updates
- **Template Management**: Environment templates can be cloned and customized through UI
- **Volume Persistence**: Named Docker volumes for workspace data persistence
- **Multi-Platform Support**: Cross-platform scripts (`.sh` and `.ps1`) for Vagrant environments