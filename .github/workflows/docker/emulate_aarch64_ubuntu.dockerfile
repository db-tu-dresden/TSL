FROM ubuntu:24.04

ENV TZ=Europe/Berlin \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    apt-get install -y --no-install-recommends bash qemu-user qemu-user-static && \
    apt-get clean && rm -rf /var/lib/pat/lists/* && \
    mkdir -p /tsl

WORKDIR /tsl