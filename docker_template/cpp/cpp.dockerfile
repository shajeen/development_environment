FROM gcc:latest

LABEL maintainer="Shajeen Ahamed <shajeenahmed@gmail.com>"

# Install necessary packages
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
        python3-pip \
        libgtest-dev && \
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

# Install Conan in a virtual environment and configure profiles
RUN python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install conan && \
    mkdir -p /home/dev/.conan && \
    /venv/bin/conan profile detect --force

# Expose SSH port
EXPOSE 22

# Set environment so that Conan and tools are in PATH
ENV PATH="/venv/bin:$PATH" \
    CONAN_USER_HOME="/home/dev/.conan"

# Default command
CMD ["/usr/sbin/sshd", "-D"]