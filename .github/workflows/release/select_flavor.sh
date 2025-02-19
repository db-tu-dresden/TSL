#!/bin/bash

PWD=$(pwd)
DETECT_FLAGS_ROOT=${1:-PWD}
LOG=$2

do_log() {
  if [[ $LOG == "--log" ]]; then
    echo "$1" >> select_flavor.log
  fi
}

tsl_folders=(
$<< TslFolderArrayValues >>
)

default_flags=(
$<< DefaultFlagsArrayValues >>
)

alternative_flags=(
$<< AlternativeFlagsArrayValues >>
)

alternative_mappings=(
$<< AlternativeMappingsArrayValues >>
)

generic_fallback=$<< GenericFallback >>

available_flags=($(${DETECT_FLAGS_ROOT}/detect_flags.sh))

# Function to check if all values in the predefined flags are present in the flags set from the system
# first argument are the predefined flags as space separated string
prefilter() {
  local predefined_flags_array=($1)
  do_log "[prefilter]: ${predefined_flags_array[@]}"
  for flag in "${predefined_flags_array[@]}"; do
    local found=0
    for avail_flag in "${available_flags[@]}"; do
      if [[ "${flag}" == "${avail_flag}" ]]; then
        found=1
        break
      fi
    done
    if [[ "${found}" -eq 0 ]]; then
      do_log "[prefilter]: ${flag} not found in available flags"
      echo 1
      return
    else
      do_log "[prefilter]: ${flag} found in available flags"
    fi
  done
  echo 0
}


# Function to calculate overlap between predefined flags and flags set from the system (higher is better)
# returns -1 if the prefilter fails
# first argument are the predefined flags as space separated string
calculate_overlap() {
  if [[ $(prefilter "$1") -ne 0 ]]; then
    do_log "[calculate_overlap]: prefilter failed"
    echo -1
    return
  fi

  local predefined_flags_array=($1)
  local overlap=0
  do_log "[calculate_overlap]: Predefined flags = ${predefined_flags_array[@]}"
  do_log "[calculate_overlap]: Available flags = ${available_flags[@]}"
  for flag in "${available_flags[@]}"; do
    for val in "${predefined_flags_array[@]}"; do
      if [[ "$flag" == "$val" ]]; then
        do_log "[calculate_overlap]: ${flag} found in predefined flags"
        ((overlap++))
      fi
    done
  done
  echo $overlap
}

# Function to find the index of the best matching predefined flags array and the system provided flags set
find_best_default_match() {
  local max_overlap=0
  local best_idx=-1

  local idx=0
  for flags_array in "${default_flags[@]}"; do
    local overlap
    do_log "[find_best_default_match]: flags_array = ${flags_array[@]}"
    overlap=$(calculate_overlap "$flags_array")
    do_log "[find_best_default_match]: overlap = ${overlap}"
    if (( overlap > max_overlap )); then
      do_log "[find_best_default_match]: found new best fit (overlap: ${max_overlap} at position ${best_idx}) ==> (overlap: ${overlap} at position ${idx})"
      max_overlap=$overlap
      best_idx=$idx
    fi
    ((idx++))
  done

  echo "${max_overlap} ${best_idx}"
}


find_best_alternative_match() {
  local max_overlap=0
  local best_idx=-1

  local idx=0
  for flags_array in "${alternative_flags[@]}"; do
    local overlap
    do_log "[find_best_alternative_match]: flags_array = ${flags_array[@]}"
    overlap=$(calculate_overlap "$flags_array")
    do_log "[find_best_alternative_match]: overlap = ${overlap}"
    if (( overlap > max_overlap )); then
      do_log "[find_best_alternative_match]: found new best fit (overlap: ${max_overlap} at position ${best_idx}) ==> (overlap: ${overlap} at position ${idx})"
      max_overlap=$overlap
      best_idx=$idx
    fi
    ((idx++))
  done

  echo "${max_overlap} ${best_idx}"
}

best_match=$(find_best_default_match)
best_match_alt=$(find_best_alternative_match)

read -r max_overlap best_idx <<< "$best_match"
read -r max_overlap_alt best_idx_alt <<< "$best_match_alt"

if ((max_overlap == 0)) && ((max_overlap_alt == 0)); then
  echo "No suitable flavor found, falling back to generic (scalar only). If you think that is a mistake, please contact the developers." > /dev/stderr
  echo "${generic_fallback}"
  exit 0
fi
if ((max_overlap > max_overlap_alt)); then
  echo ${tsl_folders[$best_idx]}
else
  echo ${alternative_mappings[$best_idx_alt]}
fi
exit 0