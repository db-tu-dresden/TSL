#!/bin/bash
CC=icx CXX=icpx cmake -B build -S . -DCMAKE_BUILD_TYPE=Release
cmake --build build
```