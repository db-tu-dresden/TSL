#!/bin/bash
# get absolute path of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Run the generator with default settings
cmake -S ${SCRIPT_DIR} -B ${SCRIPT_DIR}/build
cmake --build ${SCRIPT_DIR}/build --target Example
