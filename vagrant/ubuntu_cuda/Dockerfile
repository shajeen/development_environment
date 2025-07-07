FROM nvidia/cuda:12.3.1-devel-ubuntu22.04 

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

# Set up a new user 'vagrant' with password 'vagrant' and sudo privileges
RUN useradd -ms /bin/bash vagrant && \
    echo 'vagrant:vagrant' | chpasswd && \
    usermod -aG sudo vagrant

# Add the SSH public key to the vagrant user's authorized_keys
COPY ssh/id_rsa.pub /home/vagrant/.ssh/authorized_keys
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
