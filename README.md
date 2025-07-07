# Development Environment Setup

This repository provides a structured approach to setting up various development environments using Docker and Vagrant. It includes configurations for C++, CUDA, and Python, designed to streamline your development workflow.

## Project Structure

- `docker/`: Contains Dockerfile and docker-compose configurations for different development environments (C++, CUDA, Python).
- `vagrant/`: Contains Vagrant configurations for setting up virtual machines with various environments (Ubuntu, Ubuntu CUDA, Ubuntu CUDA VNC, C++, Python).
- `workspaces/`: Example workspace configurations, such as a Python CUDA environment.
- `docs/`: Documentation, including detailed initialization instructions.

## Getting Started

To get started with setting up your development environment, please refer to the detailed initialization guide:

[How to Initialize Your Development Environment](docs/howto_init.md)

## Environments Available

### Docker Environments

- **C++ Development:** A Docker container with GCC, CMake, Git, GDB, Clang, LLVM, Valgrind, and Conan.
- **CUDA Development:** A Docker container with NVIDIA CUDA, CUDNN, and essential development tools for GPU programming.
- **Python Development:** A Docker container with Python 3.14, essential build tools, and SSH access.

### Vagrant Environments

- **Ubuntu Base:** A basic Ubuntu virtual machine.
- **Ubuntu CUDA:** An Ubuntu virtual machine with CUDA pre-installed.
- **Ubuntu CUDA VNC:** An Ubuntu virtual machine with CUDA and VNC for graphical access.
- **C++ Development:** A Vagrant box with a C++ development environment.
- **Python Development:** A Vagrant box with a Python development environment.

## Contributing

If you wish to contribute to this project, please follow these steps:
1. Fork the repository.
2. Create a new branch for your features or bug fixes.
3. Make your changes and ensure they adhere to the existing code style.
4. Write clear and concise commit messages.
5. Submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
