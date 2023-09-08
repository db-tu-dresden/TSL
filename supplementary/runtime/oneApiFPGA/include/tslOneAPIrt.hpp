#ifndef TSL_SUPPLEMENTARY_RUNTIME_ONEAPIFPGA_TSLONEAPIRT_HPP
#define TSL_SUPPLEMENTARY_RUNTIME_ONEAPIFPGA_TSLONEAPIRT_HPP

#include <cstdlib>
#include <iostream>
#include <cstring>
#include <type_traits>
#include <string_view>
#include <climits>
#include <CL/sycl.hpp>
#include <sycl/ext/intel/fpga_extensions.hpp>

/**
 * @brief This is a workaround to handle the fact that fpga_loop_fuse_independent was first introduced with oneAPI 2022.2 (compiler release 2022.1.0)
 */
namespace sycl::ext::intel {
  namespace tsl_helper_details {
    struct incomplete_helper;
  }
  template<int N = 1, typename F>
  std::enable_if_t<std::is_same_v<F, tsl_helper_details::incomplete>> fpga_loop_fuse(F f) = delete;
  // Helper type to detect the presence of fpga_loop_fuse
  template <typename F>
  struct tsl_helper_has_fpga_loop_fuse {
    template <typename Fun>
    static auto test(int) -> decltype(fpga_loop_fuse<int{}>(std::declval<Fun>()), std::true_type{});
    template <typename>
    static auto test(...) -> std::false_type;

    using type = decltype(test<F>(0));
    static constexpr bool value = type::value;
  };

  template <int N = 1, typename Fun>
  __attribute__((always_inline)) inline auto tsl_helper_loop_fuse(Fun f, int) -> std::enable_if_t<tsl_helper_has_fpga_loop_fuse<Fun>::value> {
    fpga_loop_fuse<N>(f);
  }
  template <int N = 1, typename Fun>
  __attribute__((always_inline)) inline void tsl_helper_loop_fuse(Fun f, double) {
    f();
  }
  

  template<int N = 1, typename F>
  std::enable_if_t<std::is_same_v<F, tsl_helper_details::incomplete>> fpga_loop_fuse_independent(F f) = delete;
  template <typename F>
  struct tsl_helper_has_fpga_loop_fuse_independent {
    template <typename Fun>
    static auto test(int) -> decltype(fpga_loop_fuse_independent<int{}>(std::declval<Fun>()), std::true_type{});
    template <typename>
    static auto test(...) -> std::false_type;

    using type = decltype(test<F>(0));
    static constexpr bool value = type::value;
  };

  template <int N = 1, typename Fun>
  __attribute__((always_inline)) inline auto tsl_helper_loop_fuse_independent(Fun f, int) -> std::enable_if_t<tsl_helper_has_fpga_loop_fuse<Fun>::value> {
    fpga_loop_fuse<N>(f);
  }
  template <int N = 1, typename Fun>
  __attribute__((always_inline)) inline void tsl_helper_loop_fuse_independent(Fun f, double) {
    f();
  }
}

namespace tsl {
  namespace oneAPI {

    template <int N = 1, typename Fun>
    __attribute__((always_inline)) inline void loop_fuse(Fun f) {
      sycl::ext::intel::tsl_helper_loop_fuse<N>(f, 0);
    }
    template <int N = 1, typename Fun>
    __attribute__((always_inline)) inline void loop_fuse_independent(Fun f) {
      sycl::ext::intel::tsl_helper_loop_fuse_independent<N>(f, 0);
    }

    struct MEMORY_ON_HOST{};
    struct MEMORY_ON_DEVICE{};

    namespace details {      
      template <typename T, typename = void>
      struct multi_ptr_base_type {
          using type = typename T::value_type;
      };
      template <typename T>
      struct multi_ptr_base_type<T, std::void_t<typename T::element_type>> {
          using type = typename T::element_type;
      };
    }
    template<class MultiPtrClass>
    using multi_ptr_base_type = typename details::multi_ptr_base_type<MultiPtrClass>::type;

    template<typename T>
    using memory_base_type =
      std::conditional_t<
        std::is_pointer_v<std::remove_reference_t<T>>,
        std::remove_pointer_t<std::remove_reference_t<T>>,
        multi_ptr_base_type<std::remove_reference_t<T>>
      >;
  }
  namespace runtime {

    class oneAPI_helper {
      protected:
        static void exception_handler(sycl::exception_list exceptions) {
          for (std::exception_ptr const& e : exceptions) {
            try {
              std::rethrow_exception(e);
            } catch (sycl::exception const& e) {
              std::cerr << "Caught asynchronous SYCL exception:\n"
                        << e.what() << std::endl;
              std::terminate();
            }
          }
        }
    };
    struct oneAPI_emulator_selector: public oneAPI_helper {
      #ifdef SYCL_SELECTOR_CLASS_DEPRECATED
      sycl::queue q;
      oneAPI_emulator_selector(auto&& one_api_queue_properties)
      : q{sycl::ext::intel::fpga_emulator_selector_v, oneAPI_helper::exception_handler,  one_api_queue_properties} {
        std::cout << "Using FPGA Emulator with fpga_emulator_selector_v" << std::endl;
      }
      #else
      sycl::ext::intel::fpga_emulator_selector selector;
      sycl::queue q;
      oneAPI_emulator_selector(auto&& one_api_queue_properties)
      : selector{},
        q{selector, oneAPI_helper::exception_handler,  one_api_queue_properties} {
        std::cout << "Using FPGA Emulator with fpga_emulator_selector" << std::endl;
      }
      #endif
    };
    struct oneAPI_hardware_selector: public oneAPI_helper {
      #ifdef SYCL_SELECTOR_CLASS_DEPRECATED
      sycl::queue q;
      oneAPI_hardware_selector(auto&& one_api_queue_properties)
      : q{sycl::ext::intel::fpga_selector_v, oneAPI_helper::exception_handler,  one_api_queue_properties} {
        std::cout << "Using FPGA Hardware with fpga_selector_v" << std::endl;
      }
      #else
      sycl::ext::intel::fpga_selector selector;
      sycl::queue q;
      oneAPI_hardware_selector(auto&& one_api_queue_properties)
      : selector{},
        q{selector, oneAPI_helper::exception_handler,  one_api_queue_properties} {
        std::cout << "Using FPGA Hardware with fpga_selector" << std::endl;
      }
      #endif
    };
    
    template<typename Selector>
    class oneAPI_fpga {
      private:
        Selector selector;
        sycl::queue& q;
      public:
        oneAPI_fpga(
          auto&& one_api_queue_properties
        ):  selector{one_api_queue_properties}, 
            q{selector.q} 
        {
          // make sure the device supports USM device allocations
          sycl::device d = q.get_device();
          if (!d.get_info<sycl::info::device::usm_device_allocations>()) {
              std::cerr << "ERROR: The selected device does not support USM device"
                        << " allocations" << std::endl;
              std::terminate();
          }
          if (!d.get_info<sycl::info::device::usm_host_allocations>()) {
              std::cerr << "ERROR: The selected device does not support USM host"
                        << " allocations" << std::endl;
              std::terminate();
          }
        }
      public:
        template<typename _T>
          auto allocate(size_t element_count, ::tsl::oneAPI::MEMORY_ON_HOST, size_t alignment = 0) {
            using T = std::remove_pointer_t<std::remove_reference_t<_T>>;
            T * buffer;
            if (alignment == 0) {
              if ((buffer = sycl::malloc_host<T>(element_count*sizeof(T), q)) == nullptr) {
                std::cerr << "ERROR: could not allocate space on host" << std::endl;
                std::terminate();
              }
            } else {
              if ((buffer = sycl::aligned_alloc_host<T>(alignment, element_count*sizeof(T), q)) == nullptr) {
                std::cerr << "ERROR: could not allocate space on host" << std::endl;
                std::terminate();
              }
            }
            return sycl::host_ptr<T>{buffer};
          }
        template<typename _T>
          auto allocate(size_t element_count, ::tsl::oneAPI::MEMORY_ON_DEVICE, size_t alignment = 0) {
            using T = std::remove_pointer_t<std::remove_reference_t<_T>>;
            T * buffer;
            if (alignment == 0) {
              if ((buffer = sycl::malloc_device<T>(element_count*sizeof(T), q)) == nullptr) {
                std::cerr << "ERROR: could not allocate space on host" << std::endl;
                std::terminate();
              }
            } else {
              if ((buffer = sycl::aligned_alloc_device<T>(alignment, element_count*sizeof(T), q)) == nullptr) {
                std::cerr << "ERROR: could not allocate space on host" << std::endl;
                std::terminate();
              }
            }
            return sycl::device_ptr<T>{buffer};
          }
        template<typename T>
          void deallocate(T ptr) {
            if constexpr(std::is_pointer_v<std::remove_reference_t<T>>) {
              sycl::free(ptr, q);
            } else {
              sycl::free(ptr.get(), q);
            }               
          }
        template<typename OutT, typename InT>
          void copy(OutT out, InT in, size_t element_count) {     
            if constexpr( //If pointers are passed to copy, we could use them directly, since we assume them to be raw pointers. This is quite shaky, but it works for now.
              std::is_pointer_v<std::remove_reference_t<OutT>> &&
              std::is_pointer_v<std::remove_reference_t<InT>>
            ) {
              using InBaseT = typename std::remove_pointer_t<std::remove_reference_t<InT>>;
              q.memcpy(out, in, element_count * sizeof(InBaseT));
            } else if constexpr(std::is_pointer_v<std::remove_reference_t<OutT>>){
              using InBaseT = typename oneAPI::multi_ptr_base_type<InT>;
              q.memcpy(out, in.get(), element_count * sizeof(InBaseT));              
            } else if constexpr(std::is_pointer_v<std::remove_reference_t<InT>>) {
              using InBaseT = typename std::remove_pointer_t<std::remove_reference_t<InT>>;
              q.memcpy(out.get(), in, element_count * sizeof(InBaseT));
            } else {
              using InBaseT = typename oneAPI::multi_ptr_base_type<InT>;
              q.memcpy(out.get(), in.get(), element_count * sizeof(InBaseT));  
            }
            q.wait();
          }
        public:
          template<template<typename...> class Fun, typename... Args>
            decltype(auto) submit(Args... args) {
              return q.submit(
                [&](sycl::handler& h) {
                  h.single_task<Fun<Args...>>([=]() [[intel::kernel_args_restrict]] {
                    return Fun<Args...>::apply(args...);
                  });
                }
              ).wait();
            }
          template<typename BaseT, int VectorLength, template<typename...> class Fun, typename... Args>
            decltype(auto) submit(Args... args) {
              using FunctorClass = Fun<tsl::simd<BaseT, tsl::oneAPIfpga, sizeof(BaseT)*CHAR_BIT*VectorLength>, Args...>;
              return q.submit(
                [&](sycl::handler& h) {
                  h.single_task<FunctorClass>([=]() [[intel::kernel_args_restrict]] {
                    return FunctorClass::apply(args...);
                  });
                }
              ).wait();
            }
    };
    #ifdef ONEAPI_FPGA_HARDWARE
    using oneAPI_default_fpga = oneAPI_fpga<oneAPI_hardware_selector>;
    #else
    using oneAPI_default_fpga = oneAPI_fpga<oneAPI_emulator_selector>;
    #endif
  }
}

#endif