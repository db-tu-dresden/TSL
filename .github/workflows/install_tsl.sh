#!/bin/bash
TAR_PREFIX_TSL_DIR=tsl
TAR_PREFIX_GENERATION=generate_tsl_
TMP_DIR=$(mktemp -ud /tmp/libtsl-dev-XXXXXX)
UNPACK_DIR=${TMP_DIR}/unpacked
mkdir -p ${TMP_DIR}
mkdir -p ${UNPACK_DIR}
WORK_DIR=$(pwd)


curl -L "https://github.com/db-tu-dresden/TSL/releases/latest/download/tsl.tar.gz" -o ${TMP_DIR}/tsl.tar.gz
curl -L "https://github.com/db-tu-dresden/TSL/releases/latest/download/detect_flags.sh" -o ${TMP_DIR}/detect_flags.sh
chmod +x ${TMP_DIR}/detect_flags.sh

#create array from flags string
# AVAIL_FLAGS=($(${TMP_DIR}/detect_flags.sh))
IFS=' ' read -r -a AVAIL_FLAGS <<< "$(${TMP_DIR}/detect_flags.sh)"
unset IFS


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
  FOUND_ALL_FLAGS=1
  for i in "${!TSL_FLAGS_ARR[@]}"
  do
    FOUND_FLAG=0
    for j in "${!AVAIL_FLAGS[@]}"
    do
      if [ "${TSL_FLAGS_ARR[i]}" == "${AVAIL_FLAGS[j]}" ]; then
        FOUND_FLAG=1
        COUNTER=$((COUNTER+1))
      fi
    done
    if [ $FOUND_FLAG -eq 0 ]; then
      FOUND_ALL_FLAGS=0
      break
    fi
  done
  #if COUNTER is greater than MAX_AVAIL_FLAGS, then update MAX_AVAIL_FLAGS and CHOSEN_TSL_PATH
  if [ $COUNTER -gt $MAX_AVAIL_FLAGS ] && [ $FOUND_ALL_FLAGS -eq 1 ]; then
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

cp ${UNPACK_DIR}/${TAR_PREFIX_TSL_DIR}/${TAR_PREFIX_GENERATION}${CHOSEN_TSL_PATH}/tsl.hpp ${WORK_DIR}
