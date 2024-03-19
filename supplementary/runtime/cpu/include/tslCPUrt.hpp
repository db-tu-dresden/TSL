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
      private:
        template<int SimdSize>
        struct simd_ext_helper_t;
        {% for avail_extension_type_size in avail_extension_types_dict %}
        template<>
        struct simd_ext_helper_t<{{ avail_extension_type_size }}> { 
          using extension_t = {{ avail_extension_types_dict[avail_extension_type_size] }};
        };
        {% endfor %}
      public:
        template<typename T, int Par>
        using simd_ext_t = 
          std::conditional_t<
            (Par==1), scalar, typename cpu::simd_ext_helper_t<sizeof(T)*CHAR_BIT*Par>::extension_t>;

        using max_width_extension_t = {{ avail_extension_types_dict[avail_extension_types_dict.keys()|max] }};
        using min_width_extension_t = {{ avail_extension_types_dict[avail_extension_types_dict.keys()|min] }};
        using available_extensions_tuple = 
          std::tuple< 
            scalar,
            {% for key in avail_extension_types_dict.keys() | sort %}
            {{avail_extension_types_dict[key]}}{% if not loop.last %}, 
            {% endif %}
            {% endfor %} 
          > ;
        template<typename T>
        using available_vector_processing_styles_tuple = 
          std::tuple< 
            simd<T, scalar>,
            {% for key in avail_extension_types_dict.keys() | sort %}
            simd<T, {{avail_extension_types_dict[key]}}>{% if not loop.last %}, 
            {% endif %}
            {% endfor %} 
          > ;
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
        template<class Functor, typename... Args>
        decltype(auto) submit(Functor& fun, Args... args) {
          return fun(args...);
        }
        template<class Functor, typename... Args>
        decltype(auto) submit(Functor&& fun, Args... args) {
          return fun(args...);
        }
        template<VectorProcessingStyle PS, template<typename...> class Fun, typename... Args>
          decltype(auto) submit(Args... args) {
            return Fun<PS, Args...>::apply(args...);
          }
        template<template<typename...> class Fun, typename... Args>
          decltype(auto) submit(Args... args) {
            return Fun<Args...>::apply(args...);
          }
        template<typename BaseT, int VectorLength, template<typename...> class Fun, typename... Args>
          decltype(auto) submit(Args... args) {
            if constexpr(VectorLength == 1) {
              return Fun<simd<BaseT, scalar>, Args...>::apply(args...);
            } 
            {% for key in avail_extension_types_dict.keys() | sort %}
            else if constexpr(sizeof(BaseT)*CHAR_BIT*VectorLength == {{ key }}) {
              return Fun<simd<BaseT, {{ avail_extension_types_dict[key] }}>, Args...>::apply(args...);
            }
            {% endfor %}
            else {
              std::cerr << "ERROR: unsupported vector length" << std::endl;
              throw std::runtime_error("unsupported vector length");
            }
          }
        template<class Fun, typename... Args>
          decltype(auto) submit(Args... args) {
            return Fun::apply(args...);
          }

        template<class Fun, typename... Args>
          decltype(auto) detach(Args... args) {
            Fun::apply(args...);
          }
        
        template<TSLArithmetic BaseT>
          static constexpr std::array<uint32_t, {{avail_extension_types_dict.keys() | length + 1}}> available_parallelism() {
          	{% set keys = avail_extension_types_dict.keys() | sort | list %}
          	return { 1, {% for i in keys %}{% if not loop.first %}, {% endif %}{{i}} / (sizeof(BaseT)*CHAR_BIT){% endfor %} };
          }

        void wait() { }
    };
  }
}
#endif

