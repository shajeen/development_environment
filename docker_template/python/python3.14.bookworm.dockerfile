FROM python:3.14.0b1-slim-bookworm

LABEL MAINTAINER="Shajeen Ahamed <shajeenahmed@gmail.com>"

# Install necessary packages using apt (Debian package manager)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssh-server \
        sudo \
        wget \
        curl \
        git \
        build-essential \
        gdb \
        passwd \
        bash && \
    rm -rf /var/lib/apt/lists/*

# Generate SSH host keys
RUN ssh-keygen -A

# Setup SSH server runtime directory
RUN mkdir -p /var/run/sshd

# Create a dev user with sudo and SSH access
RUN useradd -m -s /bin/bash dev && \
    echo "dev:devpass" | chpasswd && \
    usermod -aG sudo dev && \
    echo "dev ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    mkdir -p /home/dev/.ssh && \
    chmod 700 /home/dev/.ssh && \
    chown dev:dev /home/dev/.ssh

# Configure SSH server
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    echo "PermitUserEnvironment yes" >> /etc/ssh/sshd_config

# Create workspace directory
RUN mkdir -p /workspace && chown -R dev:dev /workspace

# Expose SSH port
EXPOSE 22

# Start SSHD
CMD ["/usr/sbin/sshd", "-D"]
