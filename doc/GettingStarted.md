# Getting Started

On this page you will learn about [TSL](#TSL) and its Generator, what it is intended for and how to utilize it.


# Introduction

### **What is TSL and what is it used for?**

TSL is a C++ Header-only Library which abstracts elemental operations on 
hardware specific instructions sets, with main focus on SIMD / vector operations.
We develop and add functionality to the TSL using a top-down approach: if we need a particular functionality for an algorithm, we find a suitable level of generality and add new capability to the library. Since we are IMDB people, we probably miss out on interesting features due to a lack of necessity. If you miss any operation relevant for your specific problem, please don't hesitate to add the functionality and contribute to the library so that everyone can benefit from! For a detailed explanation on how to contribute, see section contribute.

### **Why the indirection through a generator? Why no plain header only library?**
It is a very hard, laborious, and maybe even impossible task to design a hardware abstraction library, which suits all currently available and upcoming hardware. So we didn't even try but decided to make it considerably simple to change nearly every detail of the library provided interface and implementation. To enable such flexibility, we wrote a generator that relies on Jinja2 -- a powerful and mature template engine. 
Furthermore, while developing TSL we found, that a large potion is redundant boiler plate code. 
When looking into the generated files, this should be clear.
So to avoid writing the same boiler plate over and over again, we implemented the generator.
While this seems to be unnecessary at first glance, through (i) modern compilers also support hardware detection for auto-vectorization and (ii) non-compliant code parts can be disabled using preprocessor macros, we want to support (i) explicit vectorization and reduce the code size and compile time and increase the readability of the to be shipped library (ii).

### **What is the target plattform?**

Tested on Linux (gcc , clang) & WSL

# Setup


### 1 - Getting the repository

Clone the git repositiory of the [TSL Generator](https://github.com/db-tu-dresden/TVLGen) (or one of the forks) and navigate into your freshly cloned TVLGen directory.

~~~bash
git clone https://github.com/db-tu-dresden/TVLGen <clone directory>
cd <clone directory>
~~~

 ### 2 - Install dependencies

 For this project you need to have cmake (Version 3.13 or above) and python (Version 3.8 or above) installed.

 There are some python dependencies, which are needed to run the generator.
 Install them using pip:

~~~bash
pip3 install -r ./requirements.txt
~~~

The package pygraphviz also depends on graphviz.
So make sure to install graphviz as well.

<!-- Todo: requirements installieren, vorab graphviz-dev installieren (sudo apt isntall graphviz-dev) -->

### 3 - Run the generator

As already mentioned the generator will create the TSL library.
By default, the output is directed into the generator dir, but you can specifiy an output path like following:

~~~bash
cmake . -D GENERATOR_OUTPUT_PATH=<path to output directory> -B build/
~~~

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

# TSL

<!-- https://github.com/db-tu-dresden/TVLPrimitiveData/tree/documentation -->

Basically TSL is a collection of elementary operations, e.g. addition, multiplication, comparisons, etc., 
but also load and store operations.
Those operations are called **primitives**.
Each primitive is then mapped to hardware specific instructions using a so called **Processing Style**.

Take a look at the following example:

~~~c++
#include <tslintrin.hpp>

template<typename ps>
typename ps::base_type * add_array(typename ps::base_type * lhs, typename ps::base_type * rhs, size_t size){
    using register_type = typename ps::register_type;
    using base_type = typename ps::base_type;
    register_type lhs_vec;
    register_type rhs_vec;
    register_type result_vec;

    base_type * result = new base_type[size];

    for(size_t i = 0; i < size; i += ps::vector_element_count()){
        lhs_vec = tsl::loadu<ps>(lhs + i);
        rhs_vec = tsl::loadu<ps>(rhs + i);
        result_vec = tsl::add<ps>(lhs_vec, rhs_vec);
        tsl::storeu<ps>(result + i, result_vec);
    }
    return result;
}
~~~

This is a simple function which adds two arrays element wise.
The function is templated over a processing style, which is then used to specify the target instruction set.

As input we get two arrays of the same size and the size of the arrays.
In the function three variables are declared, which are of the type specified by the processing style.
The first two are vector registers, which are used to store the data from the arrays.
The third one stores the result vector of the addition.
After creating the result array, the function iterates over the arrays and adds the elements of the arrays element wise.
To achieve that, the function loads the data from the arrays into the vector registers.
Then those registers are handed to the tsl::add function, which adds the two vectors and stores the result in the result vector.
Finally the result vector is stored back into the result array.

We then can call the function by specifying the processing style:

~~~c++
#include <iostream>

using namespace std;

int main(){
    uint64_t size = 128;
    uint64_t * lhs = new uint64_t[size];
    uint64_t * rhs = new uint64_t[size];
    uint64_t * result;

    for(uint64_t i = 0; i < size; i++){
        lhs[i] = i;
        rhs[i] = i;
    }

    using ps = tsl::simd<uint64_t, tsl::scalar>;

    uint64_t * result2 = add_array<ps>(lhs, rhs, size);

    for(uint64_t i = 0; i < size; i++){
        cout << i << " : " << result2[i] << endl;
    }


    return 0;
}
~~~

We use the tsl::simd class to store the target instruction set.
The first template parameter is the base type of the vector operations, the second defines the vector instruction set.
In the example we use the scalar processing style, which means that no vector instructions are used.

In this case the example is equivalent to the following code:

~~~c++
uint64_t * add_array(uint64_t * lhs, uint64_t * rhs, size_t size){
    uint64_t lhs_vec;
    uint64_t rhs_vec;
    uint64_t result_vec;

    uint64_t * result = new uint64_t[size];

    for(size_t i = 0; i < size; i += 1){
        lhs_vec = *(lhs + i);
        rhs_vec = *(rhs + i);
        result_vec = lhs_vec + rhs_vec;
        *(result + i) = result_vec;
    }
    return result;
}
~~~

This version of code could be implemented less cumbersome, but this shows how the generator works.
When we look at another processing style, we can see the difference:

~~~c++
using ps = tsl::simd<uint64_t, tsl::avx512>
~~~

Only thing we have to change is the target vector extension (tsl::scalar -> tsl::avx512). Then the equivalent code would look like the following implementation:

~~~c++
uint64_t * add_array(uint64_t * lhs, uint64_t * rhs, size_t size){
    __m512i lhs_vec;
    __m512i rhs_vec;
    __m512i result_vec;

    uint64_t * result = new uint64_t[size];

    for(size_t i = 0; i < size; i += 8){
        lhs_vec = _mm512_loadu_si512(lhs + i);
        rhs_vec = _mm512_loadu_si512(rhs + i);
        result_vec = _mm512_add_epi64(lhs_vec, rhs_vec);
        _mm512_storeu_si512(result + i, result_vec);
    }
    return result;
}
~~~

> **Note**: This is not what the generator generates, but it shows what the primitive calles are substituted with.

> **Note**: This implementation is not optimal, because the input arrays are not necessarily dividable by 8. So there could be a remainder, which would need to be processed separately.

> **Note**: Another issue is the alignment of the input data. The load and store operations are unaligned, which means that the data is not necessarily aligned to the vector register size. This could lead to performance issues. For more about this, see the Alignment section.


As you can see, we can quickly switch between different vector instruction sets and don't need to reimplement the whole code.



## Alignment

- todo




# Acronyms

<a name="TSL"></a>**TSL** - Template SIMD Library (former TVL -> Template Vector Library)


# See also
[Contribution](Contribution.md) if you want to contribute to the project.

[Generator Usage](GeneratorUsage.md) if you want more information about how to use the generator directly.

