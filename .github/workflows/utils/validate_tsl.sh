#!/bin/bash
PYTHON_VERSION=$1
OUT_PATH=$2

PYTHON_PATH_NUMBER=$(sed 's/\.//g' <<< ${PYTHON_VERSION})
apt-get update && apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv
python${PYTHON_VERSION} -m venv /opt/tsl_venv_${PYTHON_PATH_NUMBER}

TEMP_DIR=$(mktemp -d)

PYTHON_BIN_PATH=/opt/tsl_venv_${PYTHON_PATH_NUMBER}/bin
PYTHON_BIN=${PYTHON_BIN_PATH}/python
PIP_BIN=${PYTHON_BIN_PATH}/pip
${PYTHON_BIN} -m pip install --upgrade pip > ${OUT_PATH}/pip_upgrade 2>&1 && \
${PIP_BIN} install -r requirements.txt > ${OUT_PATH}/pip_install 2>&1 && \
${PYTHON_BIN} --version > ${OUT_PATH}/python_version 2>&1 && \
${PYTHON_BIN} main.py -o ${TEMP_DIR}/tsl_complete > ${OUT_PATH}/tsl_log 2>&1 && \
ruff check --ignore E501,F541,F401,F841,E731 --target-version="py${PYTHON_PATH_NUMBER}" -v . > ${OUT_PATH}/ruff_check 2>&1