# Use the official Ubuntu image as the base image
FROM ubuntu:latest

# Install OpenSSH server and sudo
RUN apt-get update && \
    apt-get install -y openssh-server sudo && \
    mkdir /var/run/sshd && \
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

# Expose SSH port
EXPOSE 22

# Start SSH service
CMD ["/usr/sbin/sshd", "-D"]
