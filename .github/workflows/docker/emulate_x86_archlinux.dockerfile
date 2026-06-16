FROM archlinux:latest

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN pacman -Syu --noconfirm --needed \
        base-devel \
        go \
        git \
        curl \
        ca-certificates \
        tar \
        xz \
    && pacman -Scc --noconfirm

# Install Intel SDE directly instead of using the AUR package.
# The AUR package can fail when Intel updates/replaces the tarball
# before the PKGBUILD checksum is updated.
ARG SDE_VERSION=10.8.0-2026-03-15
ARG SDE_URL=https://downloadmirror.intel.com/915934/sde-external-10.8.0-2026-03-15-lin.tar.xz
ARG SDE_SHA256=50B320CD226ACEF7A491F5B321FC1BE3C3C7984F9E27A456E64894B5B0979DD3

RUN curl -fL --retry 3 "${SDE_URL}" -o /tmp/intel-sde.tar.xz \
    && echo "${SDE_SHA256}  /tmp/intel-sde.tar.xz" | sha256sum -c - \
    && mkdir -p /opt/intel-sde \
    && tar -xf /tmp/intel-sde.tar.xz --strip-components=1 -C /opt/intel-sde \
    && rm -f /tmp/intel-sde.tar.xz

ENV PATH="/opt/intel-sde:${PATH}"

RUN sde64 --version || sde --version

WORKDIR /tsl
