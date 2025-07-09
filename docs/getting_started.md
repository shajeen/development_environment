# Getting Started with DevEnvOps

This guide provides detailed instructions on how to set up and use DevEnvOps, your development environment orchestrator. DevEnvOps allows you to manage various development environments using Docker and Vagrant through an intuitive Graphical User Interface (GUI) or via command-line operations.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

-   **Git:** For cloning the repository.
-   **Python 3.8+:** The core application is written in Python.
-   **Docker Desktop** (or Docker Engine and Docker Compose): Required for Docker-based environments.
-   **VirtualBox** (or other Vagrant-compatible provider): Required for Vagrant-based environments.
-   **Vagrant:** For managing virtual machines.

## 1. Initial Setup

First, clone the DevEnvOps repository to your local machine and set up the Python environment:

```bash
git clone https://github.com/your-username/devenops.git # Replace with actual repo URL
cd devenops
./scripts/setup.sh
```

The `setup.sh` script will:
*   Create a Python virtual environment.
*   Install necessary Python dependencies (PyYAML).
*   Make the main application scripts executable.

## 2. Using the DevEnvOps GUI (Recommended)

The DevEnvOps GUI provides a user-friendly interface for managing your development environments.

### Starting the GUI

After running `setup.sh`, activate the virtual environment and start the GUI:

```bash
source venv/bin/activate
python src/gui/docker_manager_gui.py
```

### GUI Overview

The GUI features:
*   **Environment List:** Two listboxes (Docker Compose and Vagrant) display available environments.
*   **Environment Information Panel:** Shows details (Name, Type, Status, Port, Container, Image, Volume, SSH Command, Credentials, Description) of the selected environment.
*   **Action Buttons:** Buttons for common operations like Build, Start, Stop, Restart, Clear, SSH, Edit, Clone, Info, and Delete.
*   **Options:** Checkboxes for `No Cache (Build)`, `Remove Volumes (Clear)`, `Remove Images (Delete)`, and `Remove Volumes (Delete)`.
*   **Output Panel:** Displays logs and command outputs.

### Common Operations via GUI

1.  **Select an Environment:** Click on an environment in either the Docker Compose or Vagrant listbox. Its details will appear in the "Environment Information" panel.
2.  **Build an Environment:**
    *   Select an environment.
    *   (Optional) Check "No Cache (Build)" to rebuild images without using cache.
    *   Click the "🔨 Build" button. Output will appear in the "Output" panel.
3.  **Start an Environment:**
    *   Select an environment.
    *   Click the "🚀 Start" button. The environment will start in the background. SSH connection details will be displayed in the "Output" panel.
4.  **Stop an Environment:**
    *   Select a running environment.
    *   Click the "🛑 Stop" button.
5.  **Restart an Environment:**
    *   Select an environment.
    *   Click the "🔄 Restart" button. This will stop and then start the environment.
6.  **Clear an Environment:**
    *   Select an environment.
    *   (Optional) Check "Remove Volumes (Clear)" to also remove associated Docker volumes.
    *   Click the "🧹 Clear" button. This will stop and remove containers/VMs.
7.  **Delete an Environment:**
    *   Select an environment.
    *   (Optional) Check "Remove Volumes (Delete)" to remove associated Docker volumes.
    *   (Optional) Check "Remove Images (Delete)" to remove associated Docker images.
    *   Click the "🗑️ Delete" button. This will remove the environment's configuration and optionally its volumes and images.
8.  **SSH Connect:**
    *   Select a *running* environment.
    *   Click the "🔌 SSH" button. DevEnvOps will attempt to open an SSH connection in your default terminal. If it cannot open a new terminal, it will display the SSH command in the "Output" panel for you to run manually.
9.  **Edit an Environment:**
    *   Select an environment.
    *   Click the "✏️ Edit" button. A dialog will appear allowing you to modify its display name, path, port, container name, image name, and volume.
10. **Clone an Environment:**
    *   Select an environment.
    *   Click the "📋 Clone" button. A dialog will appear where you can provide a new unique identifier, display name, and SSH port for the cloned environment. DevEnvOps will duplicate the environment's files and update its configuration.
11. **Show Container/Image Info:**
    *   Select an environment.
    *   Click the "ℹ️ Info" button. A dialog will appear showing detailed information about the associated Docker container and image.

## 3. Advanced Usage (Command Line)

For users who prefer command-line operations or for scripting purposes, you can directly interact with Docker and Vagrant.

### Docker Environments (Manual Operations)

Navigate to the specific Docker environment directory within the `templates/docker/` folder:

```bash
cd templates/docker/<environment_name>
# e.g., cd templates/docker/cpp
# e.g., cd templates/docker/cuda
# e.g., cd templates/docker/python
```

*   **Build and Run:**
    ```bash
    docker-compose up --build -d
    ```
*   **SSH Access:**
    ```bash
    ssh dev@localhost -p <port_number>
    # e.g., ssh dev@localhost -p 3001
    ```
*   **Stop:**
    ```bash
    docker-compose down
    ```

### Vagrant Environments (Manual Operations)

Navigate to the specific Vagrant environment directory within the `templates/vagrant/` folder:

```bash
cd templates/vagrant/<environment_name>
# e.g., cd templates/vagrant/ubuntu
# e.g., cd templates/vagrant/cpp
```

*   **Start:**
    ```bash
    vagrant up
    ```
*   **SSH Access:**
    ```bash
    vagrant ssh
    ```
*   **Stop and Destroy:**
    ```bash
    vagrant destroy
    ```

## 4. Environment Templates

The `templates/` directory contains all the pre-configured Docker and Vagrant environment definitions.

### Python CUDA Workspace Example

This workspace provides a Docker-based environment for Python development with CUDA support. Its files are located at `templates/docker/python-cuda-template`.

*   **Build and Run:**
    ```bash
    cd templates/docker/python-cuda-template
    docker-compose up --build -d
    ```
*   **Access via SSH (port `3004`):**
    ```bash
    ssh dev@localhost -p 3004
    ```
*   **Stop:**
    ```bash
    docker-compose down
    ```

## Troubleshooting

For common issues and solutions, please refer to the [Troubleshooting](TROUBLESHOOTING.md) document.

If you encounter port conflicts, you can modify the `port` in the environment's configuration via the GUI's "Edit" function, or manually in `src/config/docker_environments.json` (for advanced users).

For further assistance, please refer to the main [DevEnvOps README](../README.md) or open an issue on the GitHub repository.