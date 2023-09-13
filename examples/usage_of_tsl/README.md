# Minimal Working Example
This folder contains an minimalistic example of how to integrate and use TSL in your project.
You will notice a build script, but that is just for convenience. It does not set any parameters except the default cmake call paths, and builds the example target in the end.
Same goes for the clean script, which just removes the build folder.

The cmake configure stage will download the TSL Generator again in a subfolder inside this example, as you would do it in an external project, and does not use the files in parent folders. 

## How to get TSL
This example shows a way to integrate TSL without any hassle. It utilizes the cmake fetch content feature to download TSL from github and build it as part of your project.
All you have to do is to include the tsl folder (TSL_INCLUDE_DIRECTORY) and link against the "tsl" library. Done.

## How to build TSL
The TSL is automatically generated when calling the MakeAvailable command.

## How to use TSL
Simply <b>#include <tslintin.hpp></b> in your source files and all functionallity of TSL is available in your code, like shown in main.cpp.

## How to build the example
The example is build using cmake. You can use the build script to build the example, or use the following commands:
```bash
cmake -S . -B build
cmake --build build --target Example
```

## How to run the example
The executable is located in the build folder. You can run it using the following command:
```bash
./build/Example
```
It will add two vectors of numbers and output the result. In this case we use AVX512, where you can store up to 8 64bit Inegers in one register. So two arrays of 8 numbers each can be added in one instruction. The result is then stored in a third array.
