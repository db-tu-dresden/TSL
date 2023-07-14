#ifndef TSL_SUPPLEMENTARY_ONEAPIFPGA_TSLONEAPIFPGAHELPER_HPP
#define TSL_SUPPLEMENTARY_ONEAPIFPGA_TSLONEAPIFPGAHELPER_HPP

#include <array>
#include <cstdint>
#include <cstddef>
#include <utility>


namespace tsl {
  namespace oneAPIfpgaFun {
    namespace details {
      template<typename Vec, size_t Upper, size_t... Rest>
        __attribute__((always_inline)) inline typename Vec::base_type conflictReduceImpl(typename Vec::register_type const & data, std::index_sequence<Rest...>) {
          return ((typename Vec::base_type)0 | ... | (data[Upper+1] == data[Rest] ? ((typename Vec::base_type)1 << (typename Vec::base_type)Rest) : (typename Vec::base_type)0));
        }
      template<typename Vec, size_t... Is>
        __attribute__((always_inline)) inline void conflictReduce(typename Vec::register_type & result, typename Vec::register_type const & data, std::index_sequence<Is...>) {
          ((result[Is+1] = conflictReduceImpl<Vec, Is>(data, std::make_index_sequence<Is+1>{})), ...);
        }
    }
  }
}
#endif //TSL_SUPPLEMENTARY_ONEAPIFPGA_TSLONEAPIFPGAHELPER_HPP