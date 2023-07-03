#!/bin/bash

# Run the generator with default settings
cmake -S . -B build -D GENERATOR_OUTPUT_PATH="$(pwd)/generator_output"

