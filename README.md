# DevEnvOps: Development Environment Orchestrator

DevEnvOps provides a streamlined approach to managing and orchestrating various development environments using Docker and Vagrant. It offers a unified interface to build, start, stop, and manage your C++, CUDA, and Python development workspaces, enhancing productivity and ensuring consistent setups across different projects.

## Features

*   **Unified Management:** Control both Docker and Vagrant environments from a single application.
*   **Environment Templates:** Pre-configured templates for C++, CUDA, and Python development.
*   **GUI Interface:** An intuitive graphical user interface for easy interaction.
*   **Cloning and Customization:** Easily clone existing environments and customize their configurations.
*   **Status Monitoring:** Monitor the status of your development environments at a glance.

## Getting Started

To get started with setting up your development environment, please refer to the detailed initialization guide:

[Getting Started Guide](docs/getting_started.md)

### Starting the Application

After initial setup, activate your Python virtual environment and then start the DevEnvOps application:

#### Web Application (Recommended)
```bash
source venv/bin/activate
./start_web.py
```
Then open your browser to `http://localhost:5000`

#### GUI Application (Legacy)
```bash
source venv/bin/activate
./start_gui.py
```

## Environments Available

### Docker Environments

-   **C++ Development:** A Docker container with GCC, CMake, Git, GDB, Clang, LLVM, Valgrind, and Conan.
-   **CUDA Development:** A Docker container with NVIDIA CUDA, CUDNN, and essential development tools for GPU programming.
-   **Python Development:** A Docker container with Python 3.14, essential build tools, and SSH access.

### Vagrant Environments

-   **Ubuntu Base:** A basic Ubuntu virtual machine.
-   **Ubuntu CUDA:** An Ubuntu virtual machine with CUDA pre-installed.
-   **Ubuntu CUDA VNC:** An Ubuntu virtual machine with CUDA and VNC for graphical access.
-   **C++ Development:** A Vagrant box with a C++ development environment.
-   **Python Development:** A Vagrant box with a Python development environment.

## Contributing

If you wish to contribute to this project, please follow these steps:
1.  Fork the repository.
2.  Create a new branch for your features or bug fixes.
3.  Make your changes and ensure they adhere to the existing code style.
4.  Write clear and concise commit messages.
5.  Submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.