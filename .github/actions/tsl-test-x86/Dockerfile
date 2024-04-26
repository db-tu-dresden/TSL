FROM amd64/ubuntu:22.04

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update
RUN apt-get -y install \
  build-essential lsb-release wget software-properties-common gnupg \
  g++ \
  make cmake zip file bash

RUN wget https://apt.llvm.org/llvm.sh && \
  chmod +x llvm.sh && \
  ./llvm.sh 17 && \
  update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-17 100

COPY entrypoint.sh /entrypoint.sh

LABEL org.opencontainers.image.source=https://github.com/db-tu-dresden/TSL
LABEL org.opencontainers.image.description="TSLGenerator Compilation Image for x86"
LABEL org.opencontainers.image.licenses=Apache-2.0

ENTRYPOINT ["/entrypoint.sh"]
