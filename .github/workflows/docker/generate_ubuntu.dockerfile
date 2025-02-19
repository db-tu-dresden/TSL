FROM ubuntu:24.04

ENV TZ=Europe/Berlin \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update && \
    apt-get install -y --no-install-recommends lsb-release wget curl gnupg \
    zip file bash python3 python3-venv && \
    python3 -m venv /opt/tsl_venv && \
    apt-get clean && rm -rf /var/lib/pat/lists/*

COPY requirements.txt /requirements.txt

ENV PATH=/opt/tsl_venv/bin:$PATH

RUN /opt/tsl_venv/bin/pip install --no-cache-dir -r /requirements.txt && \
    /opt/tsl_venv/bin/pip install --no-cache-dir --ignore-installed ruff yamllint && \
    mkdir -p /tsl

WORKDIR /tsl