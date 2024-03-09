FROM fedora:latest

RUN dnf -y install fedora-packager rpmdevtools util-linux

RUN mkdir -p /root/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

LABEL org.opencontainers.image.source=https://github.com/db-tu-dresden/TSL
LABEL org.opencontainers.image.description="RPM Builder for TSL"
LABEL org.opencontainers.image.licenses=Apache-2.0

COPY entrypoint.sh /entrypoint.sh
COPY tsl.spec /root/rpmbuild/SPECS/tsl.spec

ENTRYPOINT ["/entrypoint.sh"]
