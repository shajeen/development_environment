# Use the official GCC image as the base image
FROM gcc:12.4.0

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

# Create a virtual environment and install Conan
RUN python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install conan

# Set up SSH server with root login and password authentication
RUN mkdir /var/run/sshd && \
    echo 'root:root' | chpasswd && \
    sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    echo 'UseDNS no' >> /etc/ssh/sshd_config && \
    echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# Set up a new user 'vagrant' with password 'vagrant' and sudo privileges
RUN useradd -ms /bin/bash vagrant && \
    echo 'vagrant:vagrant' | chpasswd && \
    usermod -aG sudo vagrant

# Add the SSH public key to the vagrant user's authorized_keys
COPY ssh/vagrant_docker_key.pub /home/vagrant/.ssh/authorized_keys
RUN chown -R vagrant:vagrant /home/vagrant/.ssh && \
    chmod 700 /home/vagrant/.ssh && \
    chmod 600 /home/vagrant/.ssh/authorized_keys

# Create workspace directory
RUN mkdir /workspace
WORKDIR /workspace

# Expose SSH port
EXPOSE 22

# Start SSH service
CMD ["/usr/sbin/sshd", "-D"]
