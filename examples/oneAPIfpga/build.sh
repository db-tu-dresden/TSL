#!/bin/bash
#check if argument passed
if [ $# -eq 0 ]; then
    echo "No target specified. Using emulator"
    TARGET=EMULATOR
else
  #check if argument is either emu or hw
  if [ $1 != "emu" ] && [ $1 != "hw" ]; then
    echo "Invalid target (emu|hw) specified. Using emulator"
    TARGET=EMULATOR
  elif [ $1 == "emu" ]; then
    TARGET=EMULATOR
  else
    TARGET=FPGA_HARDWARE
  fi
fi
CC=icx CXX=icpx cmake -B build -S . -DCMAKE_BUILD_TYPE=Release -DTARGET=$TARGET
cmake --build build