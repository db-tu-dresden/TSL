FROM ubuntu:22.04

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update
RUN apt-get -y install bash build-essential binutils lintian debhelper dh-make devscripts

RUN mkdir -p /root/debbuild/tsl/DEBIAN
RUN mkdir -p /root/debbuild/tsl/usr/include/tsl/__hollistic

COPY control /root/debbuild/tsl/DEBIAN/control
COPY postinst /root/debbuild/tsl/DEBIAN/postinst
COPY postrm /root/debbuild/tsl/DEBIAN/postrm

COPY entrypoint.sh /entrypoint.sh

LABEL org.opencontainers.image.source=https://github.com/db-tu-dresden/TSL
LABEL org.opencontainers.image.description="DEB Builder for TSL"
LABEL org.opencontainers.image.licenses=Apache-2.0

ENTRYPOINT ["/entrypoint.sh"]