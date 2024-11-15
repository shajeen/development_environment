FROM ubuntu:latest

LABEL MAINTAINER="Shajeen Ahamed <shajeenahmed@gmail.com>"

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install common dependencies and required packages for .NET SDK
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
	lsb-release \
    curl \
    git \
    cmake \
    ninja-build \
    pkg-config \
    gcc \
    g++ \
    libicu-dev \
    libgtest-dev \
    python3 \
    python3-pip \
    ghc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
	
# Add Microsoft package repository
RUN wget https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb

# Install .NET SDK
RUN apt-get update && \
    apt-get install -y dotnet-sdk-8.0 && \
    rm -rf /var/lib/apt/lists/*

# Install Google Test (gtest)
RUN cd /usr/src/gtest && \
    cmake CMakeLists.txt && \
    make && \
    cp lib/*.a /usr/lib && \
    cd / && \
    rm -rf /var/lib/apt/lists/*

# Install Go
RUN wget https://go.dev/dl/go1.21.3.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.3.linux-amd64.tar.gz && \
    rm go1.21.3.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH=$PATH:/root/.cargo/bin

# Install Julia
RUN wget https://julialang-s3.julialang.org/bin/linux/x64/1.9/julia-1.9.3-linux-x86_64.tar.gz && \
    tar -xvzf julia-1.9.3-linux-x86_64.tar.gz && \
    mv julia-1.9.3 /opt/julia && \
    rm julia-1.9.3-linux-x86_64.tar.gz
ENV PATH=$PATH:/opt/julia/bin

# Install Mojo
RUN curl https://get.modular.com | sh - && \
    modular auth mut_7e3e1b4f9c1e4e8b9d3e3e3e3e3e3e && \
    modular install mojo

# Clean up
RUN rm -rf /var/lib/apt/lists/*

# Optional: Verify installed tools
RUN dotnet --version && \
    go version && \
    rustc --version && \
    julia --version 
