# Use the official Python 3.14 slim-bookworm image as the base image for the Python development environment.
FROM python:3.14.0b1-slim-bookworm

# Set metadata for the Docker image, including the maintainer's name and email.
LABEL MAINTAINER="Shajeen Ahamed <shajeenahmed@gmail.com>"

# Update the package list and install essential development tools and utilities.
# This includes SSH server, sudo, wget, curl, git, build tools, debugger (gdb), password utility, and bash.
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

# Generate SSH host keys for the SSH server.
RUN ssh-keygen -A

# Create a directory for the SSH daemon to run.
RUN mkdir -p /var/run/sshd

# Create a new user 'dev' with a home directory and bash as the default shell.
# Set a password for 'dev', add 'dev' to the 'sudo' group, configure sudoers for no password,
# and set up SSH directory permissions.
RUN useradd -m -s /bin/bash dev && \
    echo "dev:devpass" | chpasswd && \
    usermod -aG sudo dev && \
    echo "dev ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    mkdir -p /home/dev/.ssh && \
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

# Expose port 22 for SSH access to the container.
EXPOSE 22

# Set the default command to start the SSH daemon when the container launches.
CMD ["/usr/sbin/sshd", "-D"]

