# Dockerfile for Octopus plus AIIDA
#
# Commands
# -----------------------
# docker build --build-arg NB_UID=200 -t octopus-aiida .
#
# Dockerfile notes
# -----------------------
# * Aiida core built on Jammy
# * Cannot change WORKDIR i.e. to WORKDIR /home/aiida
#   Breaks the service startup
# * Must ensure USER aiida prior to container startup
#   Else breaks the service startup
#
# Refs
# --------------------
# AIIDA Dockerhub: https://hub.docker.com/r/aiidateam/aiida-core-with-services/tags
# AIIDA Dockerfile: https://github.com/aiidateam/aiida-prerequisites
#
# sha256:dd21fca4cc0b3aedf24ddac0cd503a5fe26acc4cdd68a182fcee0cc160cd7b48
FROM aiidateam/aiida-core-with-services:latest

ENV DEBIAN_FRONTEND noninteractive

# Note, this breaks starting up the aiida services, so one must
# switch back to aiida user at the end of the Dockerfile
USER root

# NOTE gfortran 11 will get used
RUN apt-get update && apt-get install -y  \
    curl \
    pkgconf \
    cmake \
    ninja-build \
    git \
    build-essential

RUN apt-get update && apt-get install -y  \
    libopenmpi-dev \
    libopenblas-dev \
    libopenblas-openmp-dev \
    libopenblas-pthread-dev \
    libopenblas-serial-dev

RUN apt-get update && apt-get install -y  \
    libfftw3-dev \
    libgsl-dev \
    libxc-dev \
    libmetis-dev

# Allow openMPI to run in docker
ENV OMPI_ALLOW_RUN_AS_ROOT=1
ENV OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

#Terminal colour
RUN /bin/bash -c 'echo -e "export LS_OPTIONS=\"--color=auto\"\nalias ls=\"ls \$LS_OPTIONS\"" >> /root/.bashrc'

# Shell shortcuts
RUN /bin/bash -c 'echo "alias ..=\"cd ../\"" >> /root/.bashrc'

USER aiida

# cmake packaged with OS is too old
RUN conda install cmake

# Install Octopus Serial Build
# Clone
RUN git clone --depth=1 https://gitlab.com/octopus-code/octopus.git

# Configure
RUN cd octopus && cmake --preset default --fresh -G Ninja \
    -DCMAKE_DISABLE_FIND_PACKAGE_Libxc=On \
    -DCMAKE_INSTALL_PREFIX=/lib/octopus_gcc11/release-serial

# Build
RUN cd octopus && cmake --build cmake-build-release -j 4

# Install as root
USER root
RUN cd octopus && cmake --install ./cmake-build-release

# Check tests
# ctest --test-dir ./cmake-build-release -L short-run

# Switch back user and working dir prior to spinning up DB services in the container
USER aiida

ENV PATH="/lib/octopus_gcc11/release-serial/bin:${PATH}"
