# Template SIMD Library (TSL)

## **Current Status**

### Library Generation using python

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
[![dockerio](./doc/badges/docker.io.svg)](https://github.com/db-tu-dresden/TVLGen/actions/workflows/tslgen_merge_main.yml)

---
## TSL


<!-- TODO: explain what ts is -->

---
## **Motivation**

Implementing high-performance algorithms entail - among other things - hardware near optimizations. 
That is, why most of the performance-crucial algorithms are written using C/C++. 
This language family provide the ability to facilitate hardware specific capabilities like special Instruction Set Extensions like **S**ingle **I**nstruction **M**ultiple **D**ata. 
SIMD is a standard technique to speed up compute-heavy tasks by applying the same instruction on multiple data elements in parallel (data parallelism). 

SIMD can be used indirectly by taking advantage of the "auto-vectorization" capabilities of modern compilers. 
However, to enable compilers to detect simdifiable parts, the code must be annotated and follow specific rules (see [gcc docu](https://gcc.gnu.org/projects/tree-ssa/vectorization.html), [clang docu](https://llvm.org/docs/Vectorizers.html)). 
While this seems to be a good choice at first glance, making a given code auto-vectorizable can be very laborious, since the emitted assembler instructions should be checked to ensure that SIMD was applied properly (which may differ between compilers and even different versions of the same compiler). 

Another possibility of facilitating existing hardware instructions is by explicit simdification through vendor specific libraries (see [intel](https://www.intel.com/content/www/us/en/docs/intrinsics-guide/index.html), [arm](https://developer.arm.com/architectures/instruction-sets/intrinsics/)).
Those libraries expose functions or macros (so called _intrinsics_) to access the underlying functionality. 
By using explicit simdification, a developer can ensure, that the intended hardware provided functionality is used. 
We argue, that using explicit simdification provides a developer with the necessary tools to tailor and optimize an algorithm to a specific hardware to the maximum extent.

However, using vendor specific libraries come with the downside of reduced or even nonexistent portability of the code. 
To cope with that issue, different approaches exist which fall, without loss of generality, into two categories: (i) code translation, e.g. [SIMD everywhere](https://github.com/simd-everywhere/simde), and (ii) template libraries, e.g. [Highway](https://github.com/google/highway), [xsimd](https://github.com/xtensor-stack/xsimd). 
__TSL__ falls in the latter category, providing C++-_function-templates_ which are specialized for given hardware ISAs and datatypes. 

---

## **Prerequisites**

### **1. Getting the repository**

Clone the git repositiory of the [TSL Generator](https://github.com/db-tu-dresden/TVLGen) (or one of the forks) and navigate into your freshly cloned TSLGen directory.

~~~console
user@host:~ git clone https://github.com/db-tu-dresden/TVLGen tslroot
user@host:~ cd tslroot
~~~

### **2. Initialize required environemnt**

To generate the TSL you need python and some additional python packages. You can either [manually](#custom-install) setup the environemnt or use a prebuild [docker image](#docker-install).

 #### <a id="custom-install"></a>**Install dependencies manually**

In the following section we will give an explanation on how to install the requirements for Linux environments which uses ```apt``` as package manager (Debian / Ubuntu). 
For other linux distribution you may have to adopt the package manager as well as the package names. 

~~~console
# udpate apt
user@host:~/tslroot  sudo apt update
# install TSL-generator specific dependencies
user@host:~/tslroot  sudo apt -y install python3.10 graphviz-dev
# install required CMake version
user@host:~/tslroot  sudo apt -y install cmake
# make sure, that the CMake version is at least 3.19
user@host:~/tslroot  cmake --version
# install pip
user@host:~/tslroot  python3 -m pip install --upgrade pip
~~~

As the next step, install all python dependencies for instance using pip:

~~~console
user@host:~/tslroot  pip install -r ./requirements.txt
~~~
> **Note:** Please ensure, that all packages could be installed properly, otherwise the generator may fail.

To generate and build the TSL please look at section [Host Build](#custom-build)
#### <a id="docker-install"></a>**Install docker and pull the image**

Make sure you installed the [Docker engine](https://docs.docker.com/engine/install/) properly. 
If everything is up and running, just pull the image and tag it:

~~~console
user@host:~/tslroot  docker pull jpietrzyktud/tvlgen:latest
user@host:~/tslroot  docker tag jpietrzyktud/tvlgen:latest tvlgen:latest
~~~

The provided image defines a console as entry point and exposes a path `/tslgen` as mount point for the host maschine.

### **3. Generate and build the TSL**

Depending on, whether you installed setup the environment directly on your host or you decided to use the docker image, generating (and building) the TSL works a bit differently.

### <a id="custom-build"></a>_Generate and build the TSL on your system_

As the TSL is tailored to the underlying hardware we have to provide the specification of your system to the generator.
The code shown below can be used to check what FLAGS are exposed by your hardware
~~~console
user@host:~/tslroot  LSCPU_FLAGS=$(LANG=en;lscpu|grep -i flags | tr ' ' '\n' | grep -E -v '^Flags:|^$' | sort -d | tr '\n' ' ')
user@host:~/tslroot  echo $LSCPU_FLAGS
3dnowprefetch abm acpi adx aes aperfmperf apic arat arch_capabilities arch_perfmon art avx avx2 bmi1 bmi2 bts clflush clflushopt cmov constant_tsc cpuid cpuid_fault cx16 cx8 de ds_cpl dtes64 dtherm dts epb ept ept_ad erms est f16c flexpriority flush_l1d fma fpu fsgsbase fxsr ht hwp hwp_act_window hwp_epp hwp_notify ibpb ibrs ida intel_pt invpcid invpcid_single lahf_lm lm mca mce md_clear mmx monitor movbe mpx msr mtrr nonstop_tsc nopl nx pae pat pbe pcid pclmulqdq pdcm pdpe1gb pebs pge pln pni popcnt pse pse36 pti pts rdrand rdseed rdtscp rep_good sdbg sep sgx smap smep ss ssbd sse sse2 sse4_1 sse4_2 ssse3 stibp syscall tm tm2 tpr_shadow tsc tsc_adjust tsc_deadline_timer vme vmx vnmi vpid x2apic xgetbv1 xsave xsavec xsaveopt xsaves xtopology xtpr
~~~
This list can than be passed to the generator:
~~~console
user@host:~/tslroot  python3 ./main.py --targets ${LSCPU_FLAGS} -o ./lib
# you can fillter for types, which may come in handy for fast prototyping
user@host:~/tslroot  python3 ./main.py --targets ${LSCPU_FLAGS} -o ./libUI64 --types "uint64_t"
# you can filter for primitives (mainly for development reasons)
user@host:~/tslroot  python3 ./main.py --targets ${LSCPU_FLAGS} -o ./libRNDMem --primitives "gather scatter"
# get a list of all available arguments:
user@host:~/tslroot  python3 ./main.py -h
~~~
> **Note:** If your compiler does not support C++-20 concepts, you should use the `--no-concepts` argument to avoid the generator using concepts.

A more convenient way is to use the provided top-level CMakeLists.txt to do all of this in one go:
~~~console
user@host:~/tslroot  cmake -S . -D GENERATOR_OUTPUT_PATH=<path to output directory> -B lib
~~~
> **Note:** You can pass further flags which are consumed by the generator using the `-D` notation.

Under the hood, cmake utilizes py-cpuinfo to detect system specific hardware properties (i.e. which cpu flags are available) and hand them over to the generator.
This way the generated TSL library is tailored for your system.
But you can also specify the cpu flags manually, if you want to.
For more information on how to do that, take a look at the [Generator Usage](GeneratorUsage.md) page.

<!-- Todo : switches des Generators, hilfe ausgeben, Generator direkt ausführen (was macht cmake ) -->

### 4 - Include into your project

Add the path to the generated TSL directory to your include path and include the TSL header (tslintrin.h).
In a cmake project this can be done like following:

~~~cmake
add_subdirectory(<path to TSL>)
target_link_libraries(<target> PUBLIC tsl)
target_include_directories(<target> PUBLIC <path to TSL>)
~~~

Then include the following header in your source file:

~~~cpp
#include <tslintrin.h>
~~~

> **Note:** Don't include other files from the TSL directory, as they depend on the include order of tvlintrin.h.




## Note

Our template library was formerly denotated as **T**emplate **V**ector **L**ibrary (TVL). 
However, as we are database people, we frequently experienced confusion regarding the term _Vector_ (since it is predominately associated with batched processing). 
To prevent any confusion, we decided to rename our library to **T**emplate **S**IMD **L**ibrary (TSL).

For detailed information on how to Setup and use TSLGen, please refer to the [GettingStarted](doc/GettingStarted.md) page.

For writing primitives and extensions check out our [VS-Code extension](https://marketplace.visualstudio.com/items?itemName=DBTUD.tslgen-edit)

Get the latest docker-image with:

```docker pull jpietrzyktud/tvlgen:latest```


## Todo 

- [ ] Readme
  - [ ] Explain the differences between (xsimd, ghy) and (tsl) 
