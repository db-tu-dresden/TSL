#!/bin/sh -l
# set -x
PARAM_TARGETS=$1

TARGETS=$(echo $PARAM_TARGETS | sed 's/\[//g' | sed 's/\]//g' | sed 's/ //g' | sed 's/,/ /g')
TARGETS_NAME=$(echo $TARGETS | sed 's/ /-/g' | sed 's/;/-/g' | sed 's/,/-/g')
TARGETS_ARRAY_NOTATION=$(echo $PARAM_TARGETS | sed 's/\[//g' | sed 's/\]//g' | sed 's/ //g' | sed 's/,/:/g')
echo "name=${TARGETS_NAME}" >> $GITHUB_OUTPUT

REPO_ROOT=/github/workspace

GENERATION_BASE=ci/generation/${TARGETS_NAME}
GENERATION_PATH=${REPO_ROOT}/${GENERATION_BASE}
echo "out=${GENERATION_BASE}" >> $GITHUB_OUTPUT

mkdir -p ${GENERATION_PATH}
mkdir -p ${LOG_PATH}
echo "flags: ${TARGETS_ARRAY_NOTATION}" >> ${GENERATION_PATH}/tsl.conf
echo "path: ${TARGETS_NAME}" >> ${GENERATION_PATH}/tsl.conf

cd ${REPO_ROOT}
ls -halt >> ${GENERATION_PATH}/generation.log 2>&1
python3 ${REPO_ROOT}/main.py --targets ${TARGETS} --out ${GENERATION_PATH} >>${GENERATION_PATH}/generation.log 2>&1
if [ $? -ne 0 ]; then
  echo "msg=Could not generate TSL (with $TARGETS)" >> $GITHUB_OUTPUT
  echo "success=false" >> $GITHUB_OUTPUT
  echo "failout=generation.log" >> $GITHUB_OUTPUT
  exit
fi

echo "msg=TSL can be generated (with $TARGETS)." >> $GITHUB_OUTPUT
echo "success=true" >> $GITHUB_OUTPUT