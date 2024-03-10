FROM ubuntu:latest
RUN apt-get update 
RUN apt-get -y install software-properties-common \
  build-essential checkinstall \
  g++ \
  make cmake lsb-release software-properties-common \
  python3 python3-pip python3-venv \
  git wget bash

RUN wget https://apt.llvm.org/llvm.sh && \
  chmod +x llvm.sh && \
  ./llvm.sh 17 && \
  update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-17 100

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


RUN mkdir /tslgen
COPY root.tar.gz /root.tar.gz
RUN tar -xvf /root.tar.gz -C /tslgen
RUN rm /root.tar.gz
# COPY requirements.txt /requirements.txt

RUN pip install -r /tslgen/requirements.txt
RUN pip install ruff yamllint



LABEL org.opencontainers.image.source=https://github.com/db-tu-dresden/TSL
LABEL org.opencontainers.image.description="TSLGenerator Image"
LABEL org.opencontainers.image.licenses=Apache-2.0

ENTRYPOINT ["/bin/bash"]
