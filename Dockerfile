FROM ubuntu:latest
RUN apt-get update 
RUN apt-get -y install \
    build-essential \
    checkinstall \
    cmake \
    g++ \
    clang \
    graphviz-dev \
    util-linux \
    software-properties-common

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.8 python3-pip

#Installing python dependencies
COPY requirements.txt /opt/py/requirements.txt
RUN python3 -m pip install --upgrade pip
RUN pip install ruff yamllint yamlfix
RUN pip install -r /opt/py/requirements.txt

RUN mkdir /tslgen

LABEL org.opencontainers.image.source=https://github.com/db-tu-dresden/TVLGen
LABEL org.opencontainers.image.description="TSLGenerator Image"
LABEL org.opencontainers.image.licenses=Apache-2.0

ENTRYPOINT ["/bin/bash"]