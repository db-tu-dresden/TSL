FROM amd64/ubuntu:latest

RUN apt update
RUN apt-get -y install \
  build-essential lsb-release wget software-properties-common gnupg \
  g++ \
  make cmake zip file bash

RUN wget https://apt.llvm.org/llvm.sh && \
  chmod +x llvm.sh && \
  ./llvm.sh 17 && \
  update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-17 100

LABEL org.opencontainers.image.source=https://github.com/db-tu-dresden/TSL
LABEL org.opencontainers.image.description="TSLerator Compilation Image for x86"
LABEL org.opencontainers.image.licenses=Apache-2.0

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
#ENTRYPOINT ["/bin/bash"]
