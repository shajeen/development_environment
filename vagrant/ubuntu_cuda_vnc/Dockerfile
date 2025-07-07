FROM nvidia/cuda:12.3.1-devel-ubuntu22.04 

LABEL MAINTAINER="Shajeen Ahamed <shajeenahmed@gmail.com>"

# Install necessary packages: OpenSSH server, sudo, cmake, git, and additional C++ development tools
RUN apt-get update && \
        apt-get install -y \
        openssh-server \
        sudo \
        xfce4 \
        xfce4-goodies \
        tightvncserver \
        xfce4-terminal && \
    rm -rf /var/lib/apt/lists/*

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

# Set up VNC server for user 'vagrant'
RUN su - vagrant -c "mkdir -p ~/.vnc && echo 'vagrant' | vncpasswd -f > ~/.vnc/passwd && chmod 600 ~/.vnc/passwd"

# Create a VNC startup script for XFCE
RUN echo '#!/bin/bash\n\
xrdb $HOME/.Xresources\n\
startxfce4 &' > /home/vagrant/.vnc/xstartup && \
    chmod +x /home/vagrant/.vnc/xstartup && \
    chown -R vagrant:vagrant /home/vagrant/.vnc

# Expose SSH and VNC ports
EXPOSE 22 5901

# Start SSH service and VNC server with conflict handling
CMD service ssh start && \
    # Remove any existing X lock files
    rm -f /tmp/.X1-lock /tmp/.X11-unix/X1 && \
    # Check if a VNC server is already running and kill it if necessary
    if pgrep -x "Xtightvnc" > /dev/null; then vncserver -kill :1; fi && \
    # Start the VNC server on display :1
    su - vagrant -c "vncserver :1 -geometry 1920x1080 -depth 24" && \
    # Keep the container running
    tail -f /dev/null
