FROM nvidia/cuda:12.9.0-cudnn-devel-ubuntu24.04

LABEL MAINTAINER="Shajeen Ahamed <shajeenahmed@gmail.com>"

# Install necessary packages: OpenSSH server, sudo, cmake, git, and additional C++ development tools
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

# Create a dev user with sudo and SSH access
RUN useradd -ms /bin/bash dev && \
    echo "dev:devpass" | chpasswd && \
    adduser dev sudo && \
    mkdir /home/dev/.ssh && \
    chmod 700 /home/dev/.ssh && \
    chown dev:dev /home/dev/.ssh

# Allow password authentication and no root login
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    echo "PermitUserEnvironment yes" >> /etc/ssh/sshd_config

# Create workspace and give dev user access
RUN mkdir -p /workspace && chown -R dev:dev /workspace

# Install Conan in a virtual environment
RUN python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install conan


# Expose SSH port
EXPOSE 22

# Default command
CMD ["/usr/sbin/sshd", "-D"]