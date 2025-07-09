# Use the official NVIDIA CUDA image as the base image for the CUDA development environment.
FROM nvidia/cuda:12.9.0-cudnn-devel-ubuntu24.04

# Set metadata for the Docker image, including the maintainer's name and email.
LABEL MAINTAINER="Shajeen Ahamed <shajeenahmed@gmail.com>"

# Update the package list and install essential development tools and libraries.
# This includes SSH server, build tools (cmake, git, build-essential), debuggers (gdb, clang, llvm, valgrind),
# and Python for Conan.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssh-server \
        sudo \
        cmake \
        git \
        build-essential \
        gdb \
        clang \
        llvm \
        valgrind \
        python3-venv \
        python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Setup SSH server
RUN mkdir /var/run/sshd

# Create a new user 'dev' with a home directory and bash as the default shell.
# Set a password for 'dev', add 'dev' to the 'sudo' group, and set up SSH directory permissions.
RUN useradd -ms /bin/bash dev && \
    echo "dev:devpass" | chpasswd && \
    adduser dev sudo && \
    mkdir /home/dev/.ssh && \
    chmod 700 /home/dev/.ssh && \
    chown dev:dev /home/dev/.ssh

# Configure SSH daemon:
# - Enable password authentication.
# - Prevent root login via SSH for security.
# - Allow user environment variables to be passed through SSH.
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    echo "PermitUserEnvironment yes" >> /etc/ssh/sshd_config

# Create a workspace directory and set its ownership to the 'dev' user.
RUN mkdir -p /workspace && chown -R dev:dev /workspace

# Install Conan (C/C++ package manager) in a Python virtual environment.
# Upgrade pip and install conan.
RUN python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install conan


# Expose port 22 for SSH access and port 7860 for other services to the container.
EXPOSE 22 7860

# Set the default command to start the SSH daemon when the container launches.
CMD ["/usr/sbin/sshd", "-D"]