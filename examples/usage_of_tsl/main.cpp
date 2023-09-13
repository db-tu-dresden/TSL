#include <iostream>
#include <tslintrin.hpp>

int main(){
    using ps = tsl::simd<uint64_t, tsl::avx512>;
    using reg_t = typename ps::register_type;
    uint64_t a[4] = {1, 2, 3, 4};
    uint64_t b[4] = {5, 6, 7, 8};

    reg_t v1 = tsl::loadu<ps>(a);
    reg_t v2 = tsl::loadu<ps>(b);

    reg_t v3 = tsl::add<ps>(v1, v2);

    // size 8 to avoid stack smashing error
    uint64_t c[8];
    tsl::storeu<ps>(c, v3);

    for (int i = 0; i < 4; ++i){
        std::cout << c[i] << " ";
    }
    std::cout << std::endl;

    return 0;
}