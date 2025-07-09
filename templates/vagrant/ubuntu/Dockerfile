# Use the official Ubuntu image as the base image
FROM ubuntu:latest 

LABEL MAINTAINER="Shajeen Ahamed <shajeenahmed@gmail.com>"

# Install necessary packages: OpenSSH server, sudo, cmake, git, and additional C++ development tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssh-server \
        sudo  && \
    rm -rf /var/lib/apt/lists/*

# Set up SSH server with root login and password authentication
RUN mkdir /var/run/sshd && \
    echo 'root:root' | chpasswd && \
    sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    echo 'UseDNS no' >> /etc/ssh/sshd_config && \
    echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# Set up a new user 'dev' with password 'devpass' and sudo privileges
RUN useradd -ms /bin/bash dev && \
    echo 'dev:devpass' | chpasswd && \
    usermod -aG sudo dev

# Create workspace directory
RUN mkdir /workspace
WORKDIR /workspace

# Expose SSH port
EXPOSE 22

# Start SSH service
CMD ["/usr/sbin/sshd", "-D"]
