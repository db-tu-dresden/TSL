#!/bin/bash
TAR_PREFIX_TSL_DIR=tsl
TAR_PREFIX_GENERATION=generate_tsl_
TMP_DIR=$(mktemp -ud /tmp/libtsl-dev-XXXXXX)
UNPACK_DIR=${TMP_DIR}/unpacked
mkdir -p ${TMP_DIR}
mkdir -p ${UNPACK_DIR}
WORK_DIR=$(pwd)


curl -L "https://github.com/JPietrzykTUD/tsl_ci/releases/latest/download/tsl.tar.gz" -o ${TMP_DIR}/tsl.tar.gz
#we don't need to use the GitHub Rest API
#curl -L "https://github.com/jpietrzyktud/tsl_ci/releases/download/$(curl -s "https://api.github.com/repos/jpietrzyktud/tsl_ci/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')/tsl.tar.gz" -o ${TMP_DIR}/tsl.tar.gz
LSCPU_FLAGS_STRING=$(LANG=en;lscpu | grep 'Flags:' | sed -E 's/Flags:\s*//g' | sed -E 's/\s/:/g')
#create array from flags string
AVAIL_FLAGS=(${LSCPU_FLAGS_STRING//:/ })
#unpack tsl.conf
tar -xf ${TMP_DIR}/tsl.tar.gz -C ${TMP_DIR} ${TAR_PREFIX_TSL_DIR}/tsl.conf

MAX_AVAIL_FLAGS=0
CHOSEN_TSL_PATH=""
UNKNOWN_PATH="unknown"
while read -r line1 && read -r line2; do
  #remove prefix "flags: " from line1
  TSL_FLAGS_STR=${line1#flags: }
  #create array from flags string
  TSL_FLAGS_ARR=(${TSL_FLAGS_STR//:/ })
  #remove prefix "path: " from line1
  TSL_PATH=${line2#path: }

  #if TSL_FLAGS_STR equals "UNKNOWN" then set TSL_FLAGS_ARR to "UNKNOWN"
  if [ "$TSL_FLAGS_STR" == "$UNKNOWN_PATH" ]; then
    UNKNOWN_PATH=$TSL_PATH
  fi
  COUNTER=0
  for i in "${!TSL_FLAGS_ARR[@]}"
  do
    for j in "${!AVAIL_FLAGS[@]}"
    do
      if [ "${TSL_FLAGS_ARR[i]}" == "${AVAIL_FLAGS[j]}" ]; then
        COUNTER=$((COUNTER+1))
      fi
    done
  done
  #if COUNTER is greater than MAX_AVAIL_FLAGS, then update MAX_AVAIL_FLAGS and CHOSEN_TSL_PATH
  if [ $COUNTER -gt $MAX_AVAIL_FLAGS ]; then
    MAX_AVAIL_FLAGS=$COUNTER
    CHOSEN_TSL_PATH=${TSL_PATH}
  fi
done < ${TMP_DIR}/tsl/tsl.conf
echo "CHOSEN_TSL_PATH=${CHOSEN_TSL_PATH}"

if [ "$MAX_AVAIL_FLAGS" -eq "0" ]; then
  echo "No suitable extension found on this CPU. Falling back to scalar."
  CHOSEN_TSL_PATH=$UNKNOWN_PATH
fi


tar -xf ${TMP_DIR}/tsl.tar.gz -C ${UNPACK_DIR} ${TAR_PREFIX_TSL_DIR}/${TAR_PREFIX_GENERATION}${CHOSEN_TSL_PATH}
cp -r ${UNPACK_DIR}/${TAR_PREFIX_TSL_DIR}/${TAR_PREFIX_GENERATION}${CHOSEN_TSL_PATH}/include ${WORK_DIR}

if [ -d "${UNPACK_DIR}/${TAR_PREFIX_TSL_DIR}/${TAR_PREFIX_GENERATION}${CHOSEN_TSL_PATH}/supplementary" ]; then
  cp -r ${UNPACK_DIR}/${TAR_PREFIX_TSL_DIR}/${TAR_PREFIX_GENERATION}${CHOSEN_TSL_PATH}/supplementary ${WORK_DIR}
fi

echo '\
#pragma once\n\
#include "include/tslintrin.hpp"\n\' > ${WORK_DIR}/tsl.hpp