# syntax=docker/dockerfile:1.7
# Dockerfile for Octopus plus AIIDA
#
# Commands
# -----------------------
# DOCKER_BUILDKIT=1 docker build --build-arg NB_UID=200 -t octopus-aiida .
# or build with the higher-level docker compose (see compose.yml and README.md)
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

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc-12 g++-12 gfortran-12 \
    curl \
    pkgconf \
    cmake \
    ninja-build \
    git \
    build-essential

RUN apt-get update && apt-get install -y --no-install-recommends \
    libopenblas-openmp-dev \
    libfftw3-dev \
    libgsl-dev \
    libxc-dev \
    libmetis-dev

ENV CC=gcc-12
ENV CXX=g++-12
ENV FC=gfortran-12

#Terminal colour
RUN /bin/bash -c 'echo -e "export LS_OPTIONS=\"--color=auto\"\nalias ls=\"ls \$LS_OPTIONS\"" >> /root/.bashrc'

# Shell shortcuts
RUN /bin/bash -c 'echo "alias ..=\"cd ../\"" >> /root/.bashrc'

# Required in order to start the services
USER aiida
ENV PATH="/home/aiida/.local/bin:${PATH}"

# cmake packaged with OS is too old (3.22.1)
RUN pip install cmake

# Install Octopus Serial
# Clone
RUN git clone --depth=1 https://gitlab.com/octopus-code/octopus.git

# Installation directory and add it to the PATH
ENV OCTOPUS_ROOT=/lib/octopus/release-serial
ENV PATH="${OCTOPUS_ROOT}/bin:${PATH}"

# Configure
#RUN --mount=type=cache,target=/home/aiida/octopus/cmake-build-release,uid=200,gid=200 \
#    cd octopus && cmake --preset default -G Ninja \
#      -DCMAKE_DISABLE_FIND_PACKAGE_Libxc=On \
#      -DOCTOPUS_ADIOS2=Off \
#      -DCMAKE_INSTALL_PREFIX=${OCTOPUS_ROOT}
#
## Build
#RUN --mount=type=cache,target=/home/aiida/octopus/cmake-build-release,uid=200,gid=200 \
#    cd octopus && cmake --build cmake-build-release -j "$(nproc)"
#
## Install as root
#USER root
#RUN --mount=type=cache,target=/home/aiida/octopus/cmake-build-release,uid=200,gid=200 \
#    cd /home/aiida/octopus && cmake --install ./cmake-build-release
#
## Run a single test as a sanity check
#RUN --mount=type=cache,target=/home/aiida/octopus/cmake-build-release,uid=200,gid=200 \
#    cd /home/aiida/octopus && \
#    ctest --test-dir ./cmake-build-release -R 14-silicon_shifts --output-on-failure


# Building with GCC12 because octopus release build fails with GCC11
RUN cd octopus && cmake --preset default -G Ninja \
      -DCMAKE_DISABLE_FIND_PACKAGE_Libxc=On \
      -DOCTOPUS_ADIOS2=Off \
      -DCMAKE_INSTALL_PREFIX=${OCTOPUS_ROOT}

# Build
RUN cd octopus && cmake --build cmake-build-release -j "$(nproc)"

# Install as root
USER root
RUN cd /home/aiida/octopus && cmake --install ./cmake-build-release

# Run a single test as a sanity check
RUN cd /home/aiida/octopus && \
    ctest --test-dir ./cmake-build-release -R 14-silicon_shifts --output-on-failure

# Switch back user and working dir prior to spinning up DB services in the container
USER aiida
