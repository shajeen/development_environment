# How to Initialize Your Development Environment

This guide provides detailed instructions on how to set up and use the various development environments provided in this repository. You can choose between Docker-based environments for containerized development or Vagrant-based environments for virtual machines.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Git:** For cloning the repository.
- **Docker Desktop** (or Docker Engine and Docker Compose): For Docker-based environments.
- **VirtualBox** (or other Vagrant-compatible provider): For Vagrant-based environments.
- **Vagrant:** For managing virtual machines.

## 1. Clone the Repository

First, clone this repository to your local machine:

```bash
git clone https://github.com/your-username/development_environment.git
cd development_environment
```

## 2. Docker Environments

Docker environments are ideal for lightweight, isolated development setups. Each environment is defined by a `Dockerfile` and a `docker-compose.yaml` file.

### Building and Running a Docker Environment

1.  Navigate to the specific Docker environment directory:

    ```bash
    cd docker/<environment_name>
    # e.g., cd docker/cpp
    # e.g., cd docker/cuda
    # e.g., cd docker/python
    ```

2.  Build the Docker image and start the container:

    ```bash
    docker-compose up --build -d
    ```

    - `--build`: Builds the images before starting containers.
    - `-d`: Runs containers in detached mode (in the background).

3.  To access the running container via SSH:

    The SSH port for each environment is mapped to a different host port:
    - C++: `3001`
    - CUDA: `3003`
    - Python: `4001`
    - Python CUDA Workspace: `3004`

    The default username is `dev` and the password is `devpass`.

    ```bash
    ssh dev@localhost -p <port_number>
    # e.g., ssh dev@localhost -p 3001
    ```

4.  To stop the container:

    ```bash
    docker-compose down
    ```

### Available Docker Environments:

-   **`docker/cpp`**: C++ development environment.
-   **`docker/cuda`**: CUDA development environment.
-   **`docker/python`**: Python development environment.

## 3. Vagrant Environments

Vagrant environments provide full-fledged virtual machines, suitable for more complex setups or when you need a complete OS environment.

### Starting a Vagrant Environment

1.  Navigate to the specific Vagrant environment directory:

    ```bash
    cd vagrant/<environment_name>
    # e.g., cd vagrant/ubuntu
    # e.g., cd vagrant/cpp
    ```

2.  Start the Vagrant box:

    ```bash
    vagrant up
    ```

3.  To SSH into the Vagrant box:

    ```bash
    vagrant ssh
    ```

4.  To stop and destroy the Vagrant box:

    ```bash
    vagrant destroy
    ```

### Available Vagrant Environments:

-   **`vagrant/ubuntu`**: Basic Ubuntu VM.
-   **`vagrant/ubuntu_cuda`**: Ubuntu VM with CUDA.
-   **`vagrant/ubuntu_cuda_vnc`**: Ubuntu VM with CUDA and VNC.
-   **`vagrant/cpp`**: C++ development environment VM.
-   **`vagrant/python`**: Python development environment VM.

## 4. Workspaces

The `workspaces/` directory contains example configurations for specific project types that might combine different technologies.

### Python CUDA Workspace Example

This workspace provides a Docker-based environment for Python development with CUDA support.

1.  Navigate to the workspace directory:

    ```bash
    cd workspaces/python.cuda.template
    ```

2.  Build and run the environment:

    ```bash
    docker-compose up --build -d
    ```

3.  Access via SSH (port `3004`):

    ```bash
    ssh dev@localhost -p 3004
    ```

4.  Stop the environment:

    ```bash
    docker-compose down
    ```

## Troubleshooting

-   **Port Conflicts:** If you encounter port conflicts, you can modify the `ports` mapping in the respective `docker-compose.yaml` file.
-   **Docker Build Issues:** Ensure you have enough disk space and memory allocated to Docker.
-   **Vagrant Issues:** Check Vagrant and VirtualBox logs for detailed error messages.

For further assistance, please refer to the `README.md` in the root directory or open an issue on the GitHub repository.
