#ifndef TSL_SUPPLEMENTARY_RUNTIME_CPU_TSLCPURT_HPP
#define TSL_SUPPLEMENTARY_RUNTIME_CPU_TSLCPURT_HPP
#include <cstddef>
#include <cstdlib>
#include <iostream>
#include <type_traits>
#include <climits>

namespace tsl {
  namespace runtime {
    class cpu {
      public:
        cpu() = default;
      public:
        template<typename T>
          auto allocate(size_t element_count, size_t alignment = 0) {
            T * buffer;
            if (alignment == 0) {
              if ((buffer = reinterpret_cast<T*>(malloc(element_count*sizeof(T)))) == nullptr) {
                std::cerr << "ERROR: could not allocate space on host" << std::endl;
                std::terminate();
              }
            } else {
              if ((buffer = reinterpret_cast<T*>(std::aligned_alloc(alignment, element_count*sizeof(T)))) == nullptr) {
                std::cerr << "ERROR: could not allocate space on host" << std::endl;
                std::terminate();
              }
            }
            return buffer;
          }
        template<typename T>
          void deallocate(T ptr) {
            if constexpr(std::is_pointer_v<std::remove_reference_t<T>>) {
              free(ptr);
            } else {
              std::cerr << "Can only free a pointer." << std::endl;
              std::terminate();
            }
            
          }
        template<typename OutT, typename InT>
          void copy(OutT out, InT in, size_t element_count) {
            if constexpr(
              std::is_pointer_v<std::remove_reference_t<OutT>> &&
              std::is_pointer_v<std::remove_reference_t<InT>>
            ) {
              std::memcpy(out, in, element_count*sizeof(InT));
            } else {
              for (size_t i = 0; i < element_count; ++i) {
                out[i] = in[i];
              }
            }
          }
      public:
        template<template<typename...> class Fun, typename... Args>
          decltype(auto) submit(Args... args) {
            return Fun<Args...>::apply(args...);
          }
        template<typename BaseT, int VectorLength, template<typename...> class Fun, typename... Args>
          decltype(auto) submit(Args... args) {
            if constexpr(VectorLength == 1) {
              return Fun<simd<BaseT, scalar>, Args...>::apply(args...);
            } 
            {% for avail_extension_type_size in avail_extension_types_dict %}
            else if constexpr(sizeof(BaseT)*CHAR_BIT*VectorLength == {{ avail_extension_type_size }}) {
              return Fun<simd<BaseT, {{ avail_extension_types_dict[avail_extension_type_size] }}>, Args...>::apply(args...);
            }
            {% endfor %}
            else {
              std::cerr << "ERROR: unsupported vector length" << std::endl;
              throw std::runtime_error("unsupported vector length");
            }
          }
    };
  }
}
#endif