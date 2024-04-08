#!/bin/sh -l
# set -x

PARAM_PY_VERSION=$1
PY_VERSION=$(echo $PARAM_PY_VERSION | sed 's/\.//g')

echo "name=py${PY_VERSION}" >> $GITHUB_OUTPUT

REPO_ROOT=/github/workspace

GENERATION_PATH=/tmp/tsl
mkdir -p ${GENERATION_PATH}

LOG_BASE=validation/py${PY_VERSION}
LOG_PATH=${REPO_ROOT}/${LOG_BASE}
mkdir -p ${LOG_PATH}
echo "out=${LOG_BASE}" >> $GITHUB_OUTPUT


. /py/venvs/py${PY_VERSION}/bin/activate
ruff check --ignore E501,F541,F401,F841,E731 --target-version="py${PY_VERSION}" -v . > ${LOG_PATH}/ruff.log 2>&1
if [ $? -ne 0 ]; then
  echo "msg=ruff failed" >> $GITHUB_OUTPUT
  echo "success=false" >> $GITHUB_OUTPUT
  echo "failout=ruff.log" >> $GITHUB_OUTPUT
  exit
else
  yamllint --no-warnings -d relaxed ./primitive_data > ${LOG_PATH}/yamllint.log 2>&1
  if [ $? -ne 0 ]; then
    echo "msg=yamllint failed" >> $GITHUB_OUTPUT
    echo "success=false" >> $GITHUB_OUTPUT
    echo "failout=yamllint.log" >> $GITHUB_OUTPUT
  else
    python main.py -o $GENERATION_PATH > ${LOG_PATH}/TSL.log 2>&1
    if [ $? -ne 0 ]; then
      echo "msg=TSL generation failed" >> $GITHUB_OUTPUT
      echo "success=false" >> $GITHUB_OUTPUT
      echo "failout=TSL.log" >> $GITHUB_OUTPUT
      exit
    else
      echo "msg=\"TSL can be generated successfully.\"" >> $GITHUB_OUTPUT
      echo "success=true" >> $GITHUB_OUTPUT
    fi
  fi
fi

deactivate

