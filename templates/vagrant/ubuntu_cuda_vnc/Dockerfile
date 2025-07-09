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

# Set up a new user 'dev' with password 'devpass' and sudo privileges
RUN useradd -ms /bin/bash dev && \
    echo 'dev:devpass' | chpasswd && \
    usermod -aG sudo dev

# Create workspace directory
RUN mkdir /workspace
WORKDIR /workspace

# Set up VNC server for user 'dev'
RUN su - dev -c "mkdir -p ~/.vnc && echo 'devpass' | vncpasswd -f > ~/.vnc/passwd && chmod 600 ~/.vnc/passwd"

# Create a VNC startup script for XFCE
RUN echo '#!/bin/bash\n\
xrdb $HOME/.Xresources\n\
startxfce4 &' > /home/dev/.vnc/xstartup && \
    chmod +x /home/dev/.vnc/xstartup && \
    chown -R dev:dev /home/dev/.vnc

# Expose SSH and VNC ports
EXPOSE 22 5901

# Start SSH service and VNC server with conflict handling
CMD service ssh start && \
    # Remove any existing X lock files
    rm -f /tmp/.X1-lock /tmp/.X11-unix/X1 && \
    # Check if a VNC server is already running and kill it if necessary
    if pgrep -x "Xtightvnc" > /dev/null; then vncserver -kill :1; fi && \
    # Start the VNC server on display :1
    su - dev -c "vncserver :1 -geometry 1920x1080 -depth 24" && \
    # Keep the container running
    tail -f /dev/null
