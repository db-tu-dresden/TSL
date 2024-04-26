FROM amd64/ubuntu:22.04

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update 
RUN apt-get -y install software-properties-common \
    python3-full python3-pip python3-venv \
    git wget


COPY requirements.txt /requirements.txt

RUN pip3 install --ignore-installed -r /requirements.txt  --break-system-packages

COPY entrypoint.sh /entrypoint.sh
COPY target_flags_translate.py /target_flags_translate.py

LABEL org.opencontainers.image.source=https://github.com/db-tu-dresden/TSL
LABEL org.opencontainers.image.description="TSLGenerator Generation Image"
LABEL org.opencontainers.image.licenses=Apache-2.0

ENTRYPOINT ["/entrypoint.sh"]
