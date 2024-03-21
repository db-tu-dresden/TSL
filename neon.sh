#!/bin/bash
python3 main.py --no-workaround-warnings --targets neon asimd -o tsl_lib
cmake -S . -B tsl -DUSE_EXISTING_TSL_PATH=./tsl_lib
make -j -C tsl
./tsl/tsl_lib/build/src/test/tsl_test  -r compact
