![](./doc/media/tsl_repo_logo_wide.png)



---
[![Generates with py3.8-3.12](https://github.com/JPietrzykTUD/tsl_ci/actions/workflows/generation-success.yml/badge.svg)](https://github.com/JPietrzykTUD/tsl_ci/actions/workflows/generation-success.yml)
[![Generates for x86](https://github.com/JPietrzykTUD/tsl_ci/actions/workflows/x86-generation-success.yml/badge.svg)](https://github.com/JPietrzykTUD/tsl_ci/actions/workflows/x86-generation-success.yml)
[![Generates for ARM](https://github.com/JPietrzykTUD/tsl_ci/actions/workflows/arm-generation-success.yml/badge.svg)](https://github.com/JPietrzykTUD/tsl_ci/actions/workflows/arm-generation-success.yml)

[![Builds on x86](https://github.com/JPietrzykTUD/tsl_ci/actions/workflows/x86-build-and-test-success.yml/badge.svg)](https://github.com/JPietrzykTUD/tsl_ci/actions/workflows/x86-build-and-test-success.yml)
[![Builds on ARM](https://github.com/JPietrzykTUD/tsl_ci/actions/workflows/arm-build-and-test-success.yml/badge.svg)](https://github.com/JPietrzykTUD/tsl_ci/actions/workflows/arm-build-and-test-success.yml)

[![Packaged](https://github.com/JPietrzykTUD/tsl_ci/actions/workflows/publish-latest.yml/badge.svg)](https://github.com/JPietrzykTUD/tsl_ci/actions/workflows/publish-latest.yml)
<!-- 
## **Current Status**

### Library Generation using Python

[![py38](./doc/badges/generate_py3.8.svg)](https://github.com/db-tu-dresden/TVLGen/actions/workflows/tslgen_merge_main.yml)
[![py39](./doc/badges/generate_py3.9.svg)](https://github.com/db-tu-dresden/TVLGen/actions/workflows/tslgen_merge_main.yml)
[![py310](./doc/badges/generate_py3.10.svg)](https://github.com/db-tu-dresden/TVLGen/actions/workflows/tslgen_merge_main.yml)
[![py311](./doc/badges/generate_py3.11.svg)](https://github.com/db-tu-dresden/TVLGen/actions/workflows/tslgen_merge_main.yml)

### Building on __Intel__ cores with SSE, AVX(2) and AVX512, __Ubuntu (latest)__
[![build_g++](./doc/badges/build_g++.svg)](https://github.com/db-tu-dresden/TVLGen/actions/workflows/tslgen_merge_main.yml)
[![build_clang++](./doc/badges/build_clang++.svg)](https://github.com/db-tu-dresden/TVLGen/actions/workflows/tslgen_merge_main.yml)


### Running test cases on __Intel__ cores with SSE, AVX(2) and AVX512, __Ubuntu (latest)__
[![test_g++](./doc/badges/test_g++.svg)](https://github.com/db-tu-dresden/TVLGen/actions/workflows/tslgen_merge_main.yml)
[![test_clang++](./doc/badges/test_clang++.svg)](https://github.com/db-tu-dresden/TVLGen/actions/workflows/tslgen_merge_main.yml)


### Docker image containing all requirements
[![dockerio](./doc/badges/docker.io.svg)](https://github.com/db-tu-dresden/TVLGen/actions/workflows/tslgen_merge_main.yml) -->

---

|Table of contents|
|:--|
[1. Get the TSL](#get-tsl)|
[2. Usage](#tsl-usage)|
[2.1 Integration into your project](#tsl-include)|
[2.2 Starting from scratch](#tsl-scratch)|
[3. About the TSL](#tsl-intro)|
[4. Motivation](#tsl-motivation)|
[5. Contribute](#tsl-contribute)|

---

## <a id="get-tsl"></a>Get the TSL

You can either download only the relevant C++-header files if you want to use the TSL right away, or you can download the repository.

### Download the Library

The latest release is available under [Releases](https://github.com/db-tu-dresden/TSL/releases/latest).

To download the TSL to the current working directory, just run
~~~console
user@host:~ curl -L -s "https://github.com/db-tu-dresden/TSL/releases/latest/download/install_tsl.sh" | /bin/bash
~~~

If you want to "install" the TSL (the header files will be placed at /usr/include/tsl), we prepared an `rpm` and a `deb` package.
To install the `rpm` package, run
~~~console
user@host:~ sudo dnf install -y https://github.com/db-tu-dresden/TSL/releases/latest/download/libtsl-dev.rpm
~~~

To install the `deb` package, run
~~~console
user@host:~ TSL_DEB_FNAME=$(mktemp -ud --tmpdir libtsl-dev-XXXXX.deb); curl -L -s "https://github.com/db-tu-dresden/TSL/releases/latest/download/libtsl-dev.deb" -o ${TSL_DEB_FNAME} && sudo apt install ${TSL_DEB_FNAME}
~~~

### Get the Generator

#### **1. Get the repository**
Clone the git repository of the [TSL Generator](https://github.com/db-tu-dresden/TSL) and navigate into your freshly cloned TSLGen directory.

~~~console
user@host:~ git clone https://github.com/db-tu-dresden/TSL tslroot
user@host:~ cd tslroot
~~~

#### **2. Initialize required environment**

To generate the TSL, you need Python and some additional Python packages. You can either [manually](#custom-install) set up the environment or use a prebuilt [docker image](#docker-install).

#### <a id="custom-install"></a>**Install dependencies manually (Option 1)**

In the following section, we will explain how to install the requirements for Linux environments which use ```apt``` as a package manager (Debian / Ubuntu). 
You may have to adopt the package manager and the package names for other Linux distributions. 

~~~console
# update apt
user@host:~/tslroot sudo apt update
# install TSL-generator-specific dependencies
user@host:~/tslroot sudo apt -y install python3.10 graphviz-dev python3-pip
# install the required CMake version
user@host:~/tslroot sudo apt -y install cmake
# make sure that the CMake version is at least 3.19
user@host:~/tslroot cmake --version
# install pip
user@host:~/tslroot python3 -m pip install --upgrade pip
~~~
> **Note:** If you don't have root access on your machine and you can't install graphviz-dev, please delete "pygraphviz" from the requirements.txt and pass the "--no-draw-test-dependencies" to the generator whenever you use it.

As the next step, install all Python dependencies, for instance, using pip:

~~~console
user@host:~/tslroot  pip install -r ./requirements.txt
~~~
> **Note:** Please ensure all packages can be installed correctly; otherwise, the generator may fail.


#### <a id="docker-install"></a>**Install docker and pull the image (Option 2)**

Make sure you installed the [Docker engine](https://docs.docker.com/engine/install/) properly. 
If everything is up and running, pull the image and tag it:

~~~console
user@host:~/tslroot  docker pull jpietrzyktud/tslgen:latest
user@host:~/tslroot  docker tag jpietrzyktud/tslgen:latest tslgen:latest
~~~

The provided image defines a console as an entry point and exposes a path `/tslgen` as the mount point for the host machine.

> Note: The workflow description for using docker is still _work in progress_. 

[Go back to toc](#toc)

---

## <a id="tsl-usage"></a>**Usage**

In the following section, we distinguish between two use cases: (i) using the TSL within an existing project and (ii) contributing primitives and extensions (or starting from scratch). 

### <a id="tsl-include"></a>__Using the TSL in your project__ (recommended for users)

There exist several ways to incorporate the TSL into your existing project. 
If you have a CMake project and want to integrate the TSL generation into your cmake process, find the instructions in subsection [CMake Integration](#usage-cmake-integration). <br>
If your project uses a PRE-BUILD script to set up the environment, please be referred to subsection [Explicit Include](#usage-explicit-include).<br>
For a detailed explanation about how to use the TSL in your project code, see subsection [Code Example](#usage-code-example).

### <a id="usage-cmake-integration"></a>_CMake Integration_

Assuming you have the following existing project structure:
```
project
|   CMakeLists.txt          #<-- top level CMakelists.txt of the project
|   Readme.md
|
+--+src
|  |   ...
|
+--+include
|  |   ...
|
+--+libs
+--+tools
   |
   +--+tsl
      |   main.py           #<-- TSL Generator script
      |   CMakeLists.txt    #<-- TSL Generator CMakelists.txt
      |
      +--+generator
      |
      +--+primitive_data
```

In the given scenario, `./libs` contains third-party library code, and `./tools` contains third-party tools and scripts. 
The TSL generator was added as git _submodule_, _subtree_ or simply as a _sub repository_ to `./tools/tsl`.
As you may have noticed, in the top-level directory of the TSL Generator, there is a _tsl.cmake_ file. 
This can be directly used within your project top-level CMakeLists:
~~~cmake
cmake_minimum_required(VERSION 3.16)
project(<PROJECTNAME>)
# ...
#Include the TSL cmake file.
include(tools/tsl/tsl.cmake)
#tsl.cmake exports a function which can should be used to generate the TSL
create_tsl(
  TSLGENERATOR_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/tools/tsl"
  DESTINATION "${CMAKE_CURRENT_BINARY_DIR}/tools/tsl"
)

target_include_directories(<target> PUBLIC ${TSL_INCLUDE_DIRECTORY} <target_includes>...) #[1] see explanation below
target_link_libraries(<target> INTERFACE tsl)                                             #[2] ======== "" =========
~~~
The `create_tsl` function has the following signature:
~~~cmake
create_tsl(
  [<WORKAROUND_WARNINGS>    BOOL            ] # = FALSE
  [<USE_CONCEPTS>           BOOL            ] # = FALSE
  [<CREATE_TESTS>           BOOL            ] # = FALSE
  [<DRAW_TEST_DEPENDENCIES> BOOL            ] # = FALSE
  [<TSLGENERATOR_DIRECTORY> STRING          ] # = "${CMAKE_CURRENT_SOURCE_DIR}"
  [<DESTINATION>            STRING          ] # = "${CMAKE_CURRENT_BINARY_DIR}/generator_output"
  [<TARGET_FLAGS>           <item STRING>...] # = UNDEFINED
  [<APPEND_TARGETS_FLAGS>   <item STRING>...] # = UNDEFINED
  [<PRIMITIVES_FILTER>      <item STRING>...] # = UNDEFINED
  [<DATATYPES_FILTER>       <item STRING>...] # = UNDEFINED
  [<LINK_OPTIONS>           <item STRING>...] # = UNDEFINED
  [<GENERATOR_OPTIONS>      <item STRING>...] # = UNDEFINED
)
~~~

<a id="cmake-parameters"></a><details open>
<summary><b>Parameters</b></summary>

> **_Options:_** (be aware, that these are not variables but options; so if they are specified, the value will be TRUE implicitly) <br>
> `WORKAROUND_WARNINGS`: Control, whether warnings should be emitted, if a primitive is used, that is not directly backed up by the hardware.<br>
> `USE_CONCEPTS`: By default, the TSL generator will determine whether C++20-concepts are supported by your compiler. However, if you want to disable them, you can use this flag.<br>
> `CREATE_TESTS`: The TSL contains test-cases for many of the provided primitives. If you want the tests to be generated and build, set the value to TRUE.<br>
> `DRAW_TEST_DEPENDENCIES`: You can let the TSL generator draw a dependency graph of the implemented primitive-tests. <br>
> **_Single-Value Parameters:_**<br>
> `TSLGENERATOR_DIRECTORY`: By default, the TSL generator is searched from the current source dir. However, to avoid any confusion we highly recommend to set this parameter to point to the actual TSL-Generator root folder (which contains the TSL-Generator _main.py_).<br>
> `DESTINATION`: By default, the TSL generator will emit the TSL into the cmake build directory in a sub-folder called _generator_output_. If you want to "persist" the generated TSL, you should set the value to a directory outside of the build directory.<br>
> **_List Parameters:_**<br>
> `TARGET_FLAGS`: A CMake list containing the hardware target specificiers (e.g., avx avx2 avx512f). If the parameter is not set, the function will determine the available hardware capabilities by using `py-cpuinfo` or - if it fails - with `lscpu`. <br>
> `APPEND_TARGETS_FLAGS`: If you want to generate specific targets even if they are not supported by your hardware you cann pass a list of that target specifiers here.<br>
> `PRIMITIVES_FILTER`: A list of TSL-primitive names which should be considered for generation. Specifying a subset of the available primitives may be helpful for debugging purposes or just to reduce generation and build time.<br>
> `DATATYPES_FILTER`: A list of C++ data types which should be considered for generation. As for `PRIMITIVES_FILTER` slicing the TSL to only support a subset of supported datatypes will decrease the TSL complexity and thus reduce compile time. Available values are: `uint8_t, int8_t, uint16_t, int16_t, uint32_t, int32_t, uint64_t, int64_t, float, double`.<br>
> `LINK_OPTIONS`: This list can contain additional options which should be passed to the library. The values will be used for `target_link_options`.<br>
> `GENERATOR_OPTIONS`: A list of additional options that should be passed to the TSL generator. Find a comprehensive list using `python3 main.py -h`.
</details>

Under the hood, `create_tsl` will generate the TSL and create a CMakeLists.txt in the root path of the library. 
The root path of the TSL is exported as a variable called `TSL_INCLUDE_DIRECTORY` and thus can be used from your CMakelists.txt (see listing above [1]).
This path will than be added to your cmake project using `add_subdirectory`. 
The generated CMakeLists.txt defines an INTERFACE library called `tsl` that can be used for linking your target against (see listing above [2]). <br>
For an example of how to use the TSL inside your code, see subsection [Code Example](#usage-code-example).

### <a id="usage-explicit-include"></a>_Explicit Include_

As the TSL is tailored to the underlying hardware, we must provide the system specification to the generator.
The code below can be used to check what FLAGS your hardware exposes (an i7-8550U produces the result).
~~~console
user@host:~/tsl LSCPU_FLAGS=$(LANG=en;lscpu|grep -i flags | tr ' ' '\n' | grep -E -v '^Flags:|^$' | sort -d | tr '\n' ' ')
user@host:~/tsl echo $LSCPU_FLAGS
3dnowprefetch abm acpi adx aes aperfmperf apic arat arch_capabilities arch_perfmon art avx avx2 bmi1 bmi2 bts clflush clflushopt cmov constant_tsc cpuid cpuid_fault cx16 cx8 de ds_cpl dtes64 dtherm dts epb ept ept_ad erms est f16c flexpriority flush_l1d fma fpu fsgsbase fxsr ht hwp hwp_act_window hwp_epp hwp_notify ibpb ibrs ida intel_pt invpcid invpcid_single lahf_lm lm mca mce md_clear mmx monitor movbe mpx msr mtrr nonstop_tsc nopl nx pae pat pbe pcid pclmulqdq pdcm pdpe1gb pebs pge pln pni popcnt pse pse36 pti pts rdrand rdseed rdtscp rep_good sdbg sep sgx smap smep ss ssbd sse sse2 sse4_1 sse4_2 ssse3 stibp syscall tm tm2 tpr_shadow tsc tsc_adjust tsc_deadline_timer vme vmx vnmi vpid x2apic xgetbv1 xsave xsavec xsaveopt xsaves xtopology xtpr
~~~
This list can then be passed to the generator:
~~~console
user@host:~/tsl python3 ./main.py --targets ${LSCPU_FLAGS} -o ./lib
# Of course, you can also do this in one go
user@host:~/tsl python3 ./main.py --targets $(LANG=en;lscpu|grep -i flags | tr ' ' '\n' | grep -E -v '^Flags:|^$' | sort -d | tr '\n' ' ') -o ./lib
# You can fillter for types, which may come in handy for fast prototyping
user@host:~/tsl python3 ./main.py --targets ${LSCPU_FLAGS} -o ./libUI64 --types "uint64_t"
# You can filter for primitives (mainly for development reasons)
user@host:~/tsl python3 ./main.py --targets ${LSCPU_FLAGS} -o ./libRNDMem --primitives "gather scatter"
# Get a list of all available arguments:
user@host:~/tsl python3 ./main.py -h
~~~
> **Note:** If your compiler does not support C++-20 concepts, you should use the `--no-concepts` argument to avoid the generator using concepts.

After generating the TSL to `./lib` you can include the library either using the generated `./lib/CMakeLists.txt` (see subsection [CMake Integration](#usage-cmake-integration)) or by passing the include directory to your compiler:
~~~console
user@host:~/tsl $CXX_COMPILER -Ilib/include my_main.cpp 
~~~

### <a id="usage-code-example"></a>_Code Example_
After generating and including the TSL as described above, you can use the TSL within your code.
All you have to do is to include one header file (`tslintrin.hpp`). 
The primitives and extensions reside in the namespace `tsl`. An minimal example (find more [here](doc/Examples.md)) for creating an AVX-SIMD register filled with the value 42 and writing the register to stdout is shown below.
~~~cpp
#include <tslintrin.hpp>
//Now we can access the TSL functionality through their namespace:
int main() {
  //Now we can access the TSL functionality through their namespace.
  auto _vec = tsl::set1<tsl::simd<uint32_t, tsl::avx2>>(42);
  
  { // Of course, you can also use the namespace  
    using namespace tsl;
    to_ostream<simd<uint32_t, avx2>(std::cout, _vec) << std::endl;
    // This should print the following to stdout: [42,42,42,42,42,42,42,42]
  }
  return 0;
}
~~~
> **Note:** Don't include other files from the TSL directory, as they depend on the order of includes specified by tslintrin.h.



[Go back to toc](#toc)


### <a id="tsl-scratch"></a>__Starting from scratch__ (recommended for contributors)

Assuming you have the following TSL Generator project structure:
```
tsl
|   main.py
|   CMakeLists.txt          #<-- top level CMakelists.txt of the TSL Generator
|   Readme.md
|   
+--+generator               #<-- All generator-associated files are placed here
|  |...
|
+--+supplementary           #<-- Supplementary files like RTL codes reside here
|  |...
|
+--+primitive_data
   |
   +--+extensions           #<-- Hardware extension structs are defined here
   |  |
   |  +--+simd              #<-- Hardware extension structs for SIMD processing
   |  |  |
   |  |  +--+intel          #<-- Intel specific structs (e.g., sse, avx,...)
   |  |  |
   |  |  +--+arm            #<-- ARM-specific structs (e.g., Neon)
   |  |...
   |  
   +--+primitives           #<-- TSL Primitives are defined here
      |
      |   binary.yaml       #<-- all primitives which fall in the category of __binary operations__
      |   calc.yaml         #<-- all primitives which fall in the category of __arithmetic operations__
      |   ...
```

As the TSL (+generator) is a cmake project we highly recommend using cmake to set up everything (however, if you feel like generating it directly, please see subsection [Explicit Include](#usage-explicit-include) above).
~~~console
#user@host:~/tsl cmake -S . -D GENERATOR_OUTPUT_PATH=<path to output directory> -B lib
# This will create the TSL into `./lib`
user@host:~/tsl cmake -S . -B lib
~~~

> **Note:** You can pass other flags the generator consumes using the `-D` notation. A list of available flags are listed [above](#cmake-parameters).

Under the hood, cmake utilizes py-cpuinfo to detect system-specific hardware properties (i.e., which cpu flags are available) and hand them over to the generator.
This way, the generated TSL library is tailored to your system.
But you can also specify the CPU flags manually if you want to.
For more information on how to do that, look at the [Generator Usage](GeneratorUsage.md) page.

[Go back to toc](#toc)

### <a id="tsl-tests"></a>__Build and run primitive tests__ (recommended for contributors)

If you want to build the generated TSL together with the specified tests (which are created by default), utilizing [Catch2](https://github.com/catchorg/Catch2), run the following commands after CMake:
~~~console
user@host:~/tsl make -j -C lib
user@host:~/tsl ./lib/generator_output/build/src/test/tsl_test
# <output truncated>
===============================================================================
All tests passed (968 assertions in 93 test cases)
## You can list all tests using the -l flag. On the example machine, the output looks like the following:
user@host:~/tsl ./lib/generator_output/build/src/test/tsl_test -l
#<output truncated>
  Testing primitive 'mask_equal' for sse
      [mask_equal][sse]
  Testing primitive 'convert_down' for avx2
      [avx2][convert_down]
  Testing primitive 'convert_down' for scalar
      [convert_down][scalar]
  Testing primitive 'convert_down' for sse
      [convert_down][sse]
  Testing primitive 'convert_up' for avx2
      [avx2][convert_up]
  Testing primitive 'convert_up' for scalar
      [convert_up][scalar]
  Testing primitive 'convert_up' for sse
      [convert_up][sse]
93 test cases
## And you can test specific primitives:
user@host:~/tsl ./lib/generator_output/build/src/test/tsl_test "[equal]"
Filters: [equal]
#<output truncated>
===============================================================================
All tests passed (56 assertions in 3 test cases)
## You can filter for specific extensions
user@host:~/tsl ./lib/generator_output/build/src/test/tsl_test "[avx2]"
Filters: [avx2]
#<output truncated>
===============================================================================
All tests passed (328 assertions in 31 test cases)
## And you can filter for both
user@host:~/tsl ./lib/generator_output/build/src/test/tsl_test "[equal][avx2]"
Filters: [equal][avx2]
===============================================================================
All tests passed (20 assertions in 1 test case)
~~~

[Go back to toc](#toc)

---

## <a id="tsl-intro"></a>About the TSL

TSL is a C++ _template header-only library_ that abstracts elemental operations on hardware-specific instruction sets, primarily focusing on SIMD operations. 
Consequently, you can use SIMD functionality in a hardware-agnostic way, and the library will handle the according mapping. 
The provided functionality (a.k.a. "primitives") is directly mapped to the underlying hardware or uses scalar workarounds. 
Thus, you can be sure that your code is compilable on every supported platform and does what you expect. However, the performance may differ depending on the available hardware features. 

As you may notice, this repository mainly consists of _Python_ instead of C++ code. 
We wrote a library generator rather than a "one-size-fits-all" library. 

### _Why the detour via a generator? Why is there no plain header-only library?_

First, it is an arduous, laborious, and maybe even impossible task to design a hardware abstraction library that suits all currently available and upcoming hardware. 
So we didn't even try but decided to make it considerably simple to change nearly every detail of the library-provided interface and implementation. 
We wrote a generator that relies on Jinja2 - a powerful and mature template engine to enable such flexibility. 
It is possible to "cherry-pick" the generated library through our generator. 
Consequently, the generated TSL will be tailored to your specific underlying hardware. 
You may think that this seems to be unncessary at first glance as (i) modern compilers also support hardware detection for auto-vectorization and (ii) non-compliant code parts can be disabled using preprocessor macros.
Nevertheless, we argue that explicit simdification ensures traceability and provides a high degree of freedom compared to auto-vectorization. 
Furthermore, the overall code size can be significantly decreased by hardware-tailoring and this will reduce not only the compile time but increase the readability of the to be shipped library code.

Second, as the TSL is a template library, there is a lot of redundant code (when looking into the generated files, this should be clear!). 
A generator is a perfect fit to reduce manual effort, making extending the library and adopting disruptive change requests easier.

### _Why are there missing functionalities?_

The TSL is developed to effectively explore the capabilities of SIMD for In-Memory-Databases at the [Dresden Database Research Group](wwwdb.inf.tu-dresden.de).
We develop and add functionality to the TSL using a top-down approach. If we need a particular functionality for an algorithm, we find a suitable level of generality and add new capability to the library. 
Since we are IMDB people, we may miss out on exciting features due to a lack of necessity. 
If you miss any relevant operation for your specific problem, please don't hesitate to add the functionality and contribute to the library so everyone can benefit! 
For a detailed explanation of how to contribute, see the section [Contribute](#tsl-contribute).


### _What are the target platforms?_

We tested the generator and the TSL on different Linux distributions (Centos7, Ubuntu 22.04, Arch Linux) and the WSL using Python 3.8 up to 3.11 and clang/gcc.

[Go back to toc](#toc)

---
## <a id="tsl-motivation"></a>**Motivation**

Implementing high-performance algorithms entails - among other things - hardware near optimizations. 
That is why most of the performance-crucial algorithms are written using C/C++. 
This language family provides the ability to facilitate hardware-specific capabilities like special Instruction Set Extensions, e.g., **S**ingle **I**nstruction **M**ultiple **D**ata. 
SIMD is a standard technique to speed up compute-heavy tasks by applying the same instruction on multiple data elements in parallel (data parallelism). 

SIMD can be used indirectly by taking advantage of the "auto-vectorization" capabilities of modern compilers. 
However, to enable compilers to detect simdifiable parts, the code must be annotated and follow specific rules (see [gcc docu](https://gcc.gnu.org/projects/tree-ssa/vectorization.html), [clang docu](https://llvm.org/docs/Vectorizers.html)). 
While this seems a good choice at first glance, making a given code auto-vectorizable can be very laborious since the emitted assembler instructions should be checked to ensure that SIMD was appropriately applied (which may differ between compilers and even different versions of the same compiler). 

Another possibility of facilitating existing hardware instructions is by explicit simdification through vendor-specific libraries (see [intel](https://www.intel.com/content/www/us/en/docs/intrinsics-guide/index.html), [arm](https://developer.arm.com/architectures/instruction-sets/intrinsics/)).
Those libraries expose functions or macros (so-called _intrinsics_) to access the underlying functionality. 
By using explicit simdification, a developer can ensure that the intended hardware provided functionality is used. 
Explicit simdification gives a developer the tools to tailor and optimize an algorithm to specific hardware to the maximum extent.

However, using vendor-specific libraries come with the downside of reduced or even nonexistent portability of the code. 
Multiple approaches exist to cope with the portability issue. 
Without losing generality, those approaches can be classified into two categories: (i) code translation, e.g. [SIMD everywhere](https://github.com/simd-everywhere/simde), and (ii) template libraries, e.g. [Highway](https://github.com/google/highway), [xsimd](https://github.com/xtensor-stack/xsimd). 
__TSL__ falls in the latter category, providing C++-_function-templates_ which are specialized for given hardware ISAs and datatypes. 

[Go back to toc](#toc)

---

## <a id="tsl-contribute"></a>**Contribute**

As a small group mainly focused on In-Memory-Database, we certainly miss crucial functionality needed by algorithms from other domains or even from our own. 
We would highly appreciate your contribution of your expertise and use cases through adding to the existing library. 
To help you with this, we developed a [Visual Studio Code Extension](https://marketplace.visualstudio.com/items?itemName=DBTUD.tslgen-edit) that provides helpful features like TSL-specific auto-completion, code-preview generation, ad-hoc build and testing and much more. 
We recommend using this since writing YAML files can be pretty nerve-racking sometimes ;).

[Go back to toc](#toc)

## Note

Our template library was formerly denoted as **T**emplate **V**ector **L**ibrary (TVL). 
However, database people frequently need clarification regarding the term _Vector_ (since it is predominately associated with batched processing). 
To prevent confusion, we renamed our library to **T**emplate **S**IMD **L**ibrary (TSL).

## Todo 

- [ ] Readme
  - [ ] Explain the differences between (xsimd, ghy) and (tsl) 
  - [ ] Proofread
  - [ ] Reproduce the workflow for the Prerequisites and Usage section
  - [ ] Explain how (if possible) the docker workflow can be integrated into an existing CMake-Project
