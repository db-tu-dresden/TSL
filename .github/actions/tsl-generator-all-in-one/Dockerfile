FROM ubuntu:23.04

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update 
RUN apt-get -y install software-properties-common \
  build-essential checkinstall \
  make cmake lsb-release \
  python3-full python3-pip python3-venv \
  git wget bash

# Install gcc 13
RUN add-apt-repository ppa:ubuntu-toolchain-r/test && \
    apt-get update && \
    apt-get install -y g++-13 && \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-13 100 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-13 100

# Install clang-18
RUN wget https://apt.llvm.org/llvm.sh && \
    chmod u+x llvm.sh 
RUN ./llvm.sh 17 && \
    update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-17 100

RUN mkdir /tslgen
COPY root.tar.gz /root.tar.gz
RUN tar -xvf /root.tar.gz -C /tslgen
RUN rm /root.tar.gz
# COPY requirements.txt /requirements.txt

RUN pip install --ignore-installed -r /tslgen/requirements.txt --break-system-packages
RUN pip install --ignore-installed ruff yamllint --break-system-packages



LABEL org.opencontainers.image.source=https://github.com/db-tu-dresden/TSL
LABEL org.opencontainers.image.description="TSLGenerator Image"
LABEL org.opencontainers.image.licenses=Apache-2.0

ENTRYPOINT ["/bin/bash"]
