#ifndef TSL_SUPPLEMENTARY_ONEAPIFPGA_TSLONEAPIFPGAHELPER_HPP
#define TSL_SUPPLEMENTARY_ONEAPIFPGA_TSLONEAPIFPGAHELPER_HPP

#include <array>
#include <cstdint>
#include <cstddef>
#include <utility>


namespace tsl {
  namespace oneAPIfpgaFun {
    namespace details {
      /**
        result[7] = ((data[7] == data[6]) ? 0b1000000 : 0) | ((data[7] == data[5]) ? 0b100000 : 0) | ((data[7] == data[4]) ? 0b10000 : 0) | ((data[7] == data[3]) ? 0b1000 : 0) | ((data[7] == data[2]) ? 0b100 : 0) | ((data[7] == data[1]) ? 0b10 : 0) | ((data[7] == data[0]) ? 0b1 : 0);
        result[6] = ((data[6] == data[5]) ? 0b100000 : 0) | ((data[6] == data[4]) ? 0b10000 : 0) | ((data[6] == data[3]) ? 0b1000 : 0) | ((data[6] == data[2]) ? 0b100 : 0) | ((data[6] == data[1]) ? 0b10 : 0) | ((data[6] == data[0]) ? 0b1 : 0);
        result[5] = ((data[5] == data[4]) ? 0b10000 : 0) | ((data[5] == data[3]) ? 0b1000 : 0) | ((data[5] == data[2]) ? 0b100 : 0) | ((data[5] == data[1]) ? 0b10 : 0) | ((data[5] == data[0]) ? 0b1 : 0);
        result[4] = ((data[4] == data[3]) ? 0b1000 : 0) | ((data[4] == data[2]) ? 0b100 : 0) | ((data[4] == data[1]) ? 0b10 : 0) | ((data[4] == data[0]) ? 0b1 : 0);
        result[3] = ((data[3] == data[2]) ? 0b100 : 0) | ((data[3] == data[1]) ? 0b10 : 0) | ((data[3] == data[0]) ? 0b1 : 0);
        result[2] = ((data[2] == data[1]) ? 0b10 : 0) | ((data[2] == data[0]) ? 0b1 : 0);
        result[1] = ((data[1] == data[0]) ? 0b1 : 0);
       */
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