FROM amd64/ubuntu:latest

RUN apt-get update 
RUN apt-get -y install software-properties-common \
  python3 python3-pip python3-venv \
  git wget

RUN ls 
RUN pwd

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

LABEL org.opencontainers.image.source=https://github.com/db-tu-dresden/TSL
LABEL org.opencontainers.image.description="TSLerator Generation Image"
LABEL org.opencontainers.image.licenses=Apache-2.0

COPY entrypoint.sh /entrypoint.sh
COPY target_flags_translate.py /target_flags_translate.py


ENTRYPOINT ["/entrypoint.sh"]
