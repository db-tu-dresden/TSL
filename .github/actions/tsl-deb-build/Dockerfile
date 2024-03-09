FROM ubuntu:latest

RUN apt-get update
RUN apt-get -y install bash build-essential binutils lintian debhelper dh-make devscripts

RUN mkdir -p /root/debbuild/tsl/DEBIAN
RUN mkdir -p /root/debbuild/tsl/usr/include/tsl/__hollistic

LABEL org.opencontainers.image.source=https://github.com/db-tu-dresden/TSL
LABEL org.opencontainers.image.description="DEB Builder for TSL"
LABEL org.opencontainers.image.licenses=Apache-2.0

COPY control /root/debbuild/tsl/DEBIAN/control
COPY postinst /root/debbuild/tsl/DEBIAN/postinst
COPY postrm /root/debbuild/tsl/DEBIAN/postrm

COPY entrypoint.sh /entrypoint.sh


# ENTRYPOINT [ "/bin/bash" ]
ENTRYPOINT ["/entrypoint.sh"]