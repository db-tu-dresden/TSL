FROM ubuntu:24.04

ENV TZ=Europe/Berlin \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    apt-get install -y --no-install-recommends git wget build-essential \
    g++ make cmake bash \
    gcc-aarch64-linux-gnu g++-aarch64-linux-gnu binutils-aarch64-linux-gnu binutils-aarch64-linux-gnu-dbg build-essential && \
    apt-get clean && rm -rf /var/lib/pat/lists/* && \
    wget -O - https://apt.llvm.org/llvm.sh | bash -s -- 18 && \
    update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-18 100 && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    mkdir -p /tsl

WORKDIR /tsl