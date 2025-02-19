FROM ubuntu:24.04

ENV TZ=Europe/Berlin \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get -y install --no-install-recommends \
    bash build-essential binutils lintian debhelper dh-make devscripts \
    g++ which && \
    mkdir -p /root/debbuild/tsl/DEBIAN && \
    mkdir -p /root/debbuild/tsl/usr/include/tsl/__hollistic && \
    mkdir -p /tsl

LABEL org.opencontainers.image.source=https://github.com/db-tu-dresden/TSL
LABEL org.opencontainers.image.description="DEB Builder for TSL"
LABEL org.opencontainers.image.licenses=Apache-2.0

WORKDIR /tsl