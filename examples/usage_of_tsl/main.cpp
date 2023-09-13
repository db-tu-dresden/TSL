#include <iostream>
#include <tslintrin.hpp>

int main(){
    // processing style which specifies the vector instruction set
    using ps = tsl::simd<uint64_t, tsl::avx512>;
    // register type from the processing style
    using reg_t = typename ps::register_type;
    // input data
    uint64_t a[8] = {1, 2, 3, 4, 5, 6, 7, 8};
    uint64_t b[8] = {1, 2, 3, 4, 5, 6, 7, 8};

    // load input data into registers
    reg_t v1 = tsl::loadu<ps>(a);
    reg_t v2 = tsl::loadu<ps>(b);

    // add the two vectors
    reg_t v3 = tsl::add<ps>(v1, v2);

    // store the result
    uint64_t c[8];
    tsl::storeu<ps>(c, v3);

    // print the result
    for (int i = 0; i < 8; ++i){
        std::cout << c[i] << " ";
    }
    std::cout << std::endl;

    return 0;
}