#!/bin/bash -l

COMPILER=$1
TSL_PATH=$2

REPO_ROOT=/github/workspace
TSL_ROOT=${REPO_ROOT}/${TSL_PATH}

TSL_STRIPPED=${TSL_PATH#generate/}
#transform TSL_STRIPPED to array by strings by splitting it with '-'
TSL_SUPPORTED_FLAGS=(${TSL_STRIPPED//-/ })

LSCPU_FLAGS_STRING=$(LANG=en;lscpu | grep 'Flags:' | sed -E 's/Flags:\s*//g' | sed -E 's/\s/:/g')
AVAIL_FLAGS=(${LSCPU_FLAGS_STRING//:/ })
declare -A AVAIL_MAP
for item in "${AVAIL_FLAGS[@]}"; do
  AVAIL_MAP[$item]=1
done

BUILD_AND_TEST_BASE=${TSL_PATH}/build_and_test/${COMPILER}
BUILD_AND_TEST_PATH=${TSL_ROOT}/${BUILD_AND_TEST_BASE}

LOG_BASE=${BUILD_AND_TEST_BASE}/log
LOG_PATH=${TSL_ROOT}/${LOG_BASE}
LOG_FILE=${LOG_PATH}/tsl.log
touch ${LOG_FILE}

BUILD_BASE=${BUILD_AND_TEST_BASE}/build
BUILD_PATH=${TSL_ROOT}/${BUILD_BASE}

mkdir -p ${LOG_PATH}
mkdir -p ${BUILD_PATH}

echo "out=${BUILD_AND_TEST_BASE}" >> $GITHUB_OUTPUT
echo "name=${COMPILER}" >> $GITHUB_OUTPUT

echo "Platform: $(uname -m)" >> ${LOG_FILE} 2>&1
echo "TSL_ROOT: ${TSL_ROOT}" >> ${LOG_FILE} 2>&1
ls ${TSL_ROOT} -halt >> ${LOG_FILE} 2>&1

COMPILER_BIN=$(which ${COMPILER})
COMPILER_VERSION=$(${COMPILER_BIN} --version)
echo "Compiler: ${COMPILER} (${COMPILER_BIN})" >> ${LOG_FILE} 2>&1
echo "Compiler version: ${COMPILER_VERSION}" >> ${LOG_FILE} 2>&1

echo "Building ${TSL_ROOT} (with ${COMPILER})"
echo "Building ${TSL_ROOT} (with ${COMPILER})" >> ${LOG_FILE} 2>&1
cmake -S ${TSL_ROOT} -B ${BUILD_PATH} -DCMAKE_CXX_COMPILER=${COMPILER_BIN} -DCMAKE_BUILD_TYPE=Release >> ${LOG_FILE} 2>&1
if [ $? -ne 0 ]; then
  echo "msg=cmake failed for $TSL_ROOT" >> $GITHUB_OUTPUT
  echo "success=false" >> $GITHUB_OUTPUT
  echo "failout=tsl.log" >> $GITHUB_OUTPUT
  exit
fi
cmake --build ${BUILD_PATH} --config Release >> ${LOG_FILE} 2>&1
if [ $? -ne 0 ]; then
  echo "msg=Build failed for $TSL_ROOT" >> $GITHUB_OUTPUT
  echo "success=false" >> $GITHUB_OUTPUT
  echo "failout=tsl.log" >> $GITHUB_OUTPUT
  exit
fi
echo "Done"

# strip generate/ from TSL_PATH

EXECUTABLE=${BUILD_PATH}/src/test/tsl_test
echo "Testing (${EXECUTABLE})"
echo "Executing ${EXECUTABLE}" >> ${LOG_FILE} 2>&1
file ${EXECUTABLE}
echo "file $(file ${EXECUTABLE})" >> ${LOG_FILE} 2>&1

for flag in "${TSL_SUPPORTED_FLAGS[@]}"; do
  if [[ -z "${AVAIL_MAP[$flag]}" ]]; then
    echo "msg=CPU does not support required flag for TSL_STRIPPED=${TSL_STRIPPED}" >> $GITHUB_OUTPUT
    echo "success=skipped" >> $GITHUB_OUTPUT
    echo "failout=tsl.log" >> $GITHUB_OUTPUT
    exit
  fi
done
${EXECUTABLE} >> ${LOG_FILE} 2>&1
if [ $? -ne 0 ]; then
  echo "msg=Tests failed for $TSL_ROOT" >> $GITHUB_OUTPUT
  echo "success=false" >> $GITHUB_OUTPUT
  echo "failout=tsl.log" >> $GITHUB_OUTPUT
  exit
fi
echo "Done"


echo "msg=TSL can be generated build (with $COMPILER) and all tests were green." >> $GITHUB_OUTPUT
echo "success=true" >> $GITHUB_OUTPUT
