FROM fedora:latest

RUN dnf -y install fedora-packager rpmdevtools util-linux python3 which g++ && \
    dnf clean all && \
    mkdir -p /root/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS} && \
    mkdir -p /tsl

LABEL org.opencontainers.image.source=https://github.com/db-tu-dresden/TSL
LABEL org.opencontainers.image.description="RPM Builder for TSL"
LABEL org.opencontainers.image.licenses=Apache-2.0

WORKDIR /tsl