#include <iostream>
#include "tslintrin.hpp"

template<class SimdT, typename PtrTOut, typename PtrTIn, typename SizeT>
struct count_leading_zero_kernel {
  static void apply(PtrTOut out, PtrTIn in, SizeT element_count) {
    for (size_t i = 0; i < element_count; i+=SimdT::vector_element_count()) {
      auto in_reg = tsl::loadu<SimdT>(&in[i]);
      auto result_reg = tsl::lzc<SimdT>(in_reg);
      tsl::storeu<SimdT>(&out[i], result_reg);
    }
  }
};

int main(void) {
  // so far, only 32-bit unsigned integers are supported as RTL code

  bool all_ok = true;

  using namespace tsl;
  executor<runtime::cpu> cpu_executor;
  using cpu_simd = simd<uint32_t, typename runtime::cpu::max_width_extension_t>;

  executor<runtime::oneAPI_default_fpga> fpga_executor{
      sycl::property_list{sycl::property::queue::enable_profiling()}
    };
  using fpga_simd = simd<uint32_t, oneAPIfpgaRTL, 512>;
  
  auto expected_result     = cpu_executor.allocate<uint32_t>(128);
  // allocate memory on host
  auto host_mem_data       = cpu_executor.allocate<uint32_t>(128);
  auto host_mem_result     = cpu_executor.allocate<uint32_t>(128);
  // allocate memory accessible from host and FPGA device
  // WATCH OUT: oneAPI::MEMORY_ON_HOST and oneAPI::MEMORY_ON_DEVICE will soon be moved up in the namespace hierarchy
  auto usm_host_mem_data   = fpga_executor.allocate<uint32_t>(128, oneAPI::MEMORY_ON_HOST{});
  auto usm_host_mem_result = fpga_executor.allocate<uint32_t>(128, oneAPI::MEMORY_ON_HOST{});
  // allocate memory on FPGA device
  auto usm_dev_mem_data    = fpga_executor.allocate<uint32_t>(128, oneAPI::MEMORY_ON_DEVICE{});
  auto usm_dev_mem_result  = fpga_executor.allocate<uint32_t>(128, oneAPI::MEMORY_ON_DEVICE{});

  // initialize input data
  host_mem_data[0] = 0;
  usm_host_mem_data[0] = 0;
  expected_result[0] = 32;
  for (uint32_t i = 1; i < 128; i++) {
    host_mem_data[i] = i;
    usm_host_mem_data[i] = i;
    expected_result[i] = __builtin_clz(i);
  }
  // copy input data to FPGA device
  fpga_executor.copy(usm_dev_mem_data, usm_host_mem_data, 128);
  
  // initialize output
  for (size_t i = 0; i < 128; i++) {
    host_mem_result[i] = 0;
    usm_host_mem_result[i] = 0;
  }
  // copy output to FPGA device
  fpga_executor.copy(usm_dev_mem_result, usm_host_mem_result, 128);


  // run kernel on CPU using avx512
  cpu_executor.submit<cpu_simd, count_leading_zero_kernel>(host_mem_result, host_mem_data, (size_t)128);
  // check results
  for (size_t i = 0; i < 128; i++) {
    if (host_mem_result[i] != expected_result[i]) {
      std::cerr << "ERROR: host_mem_result[" << i << "] = " << host_mem_result[i] << " != expected_result[" << i << "] = " << expected_result[i] << std::endl;
      all_ok = false;
    }
  }

  // run kernel on FPGA using oneAPIfpgaRTL (RTL code is built seperately). Use USM-Host memory
  fpga_executor.submit<fpga_simd, count_leading_zero_kernel>(usm_host_mem_result, usm_host_mem_data, (size_t)128);
  // check results
  for (size_t i = 0; i < 128; i++) {
    if (host_mem_result[i] != expected_result[i]) {
      std::cerr << "ERROR: usm_host_mem_result[" << i << "] = " << usm_host_mem_result[i] << " != expected_result[" << i << "] = " << expected_result[i] << std::endl;
      all_ok = false;
    }
  }

  // run kernel on FPGA using oneAPIfpgaRTL (RTL code is built seperately). Use USM-Device memory
  fpga_executor.submit<fpga_simd, count_leading_zero_kernel>(usm_dev_mem_result, usm_dev_mem_data, (size_t)128);

  // copy output to host
  fpga_executor.copy(usm_host_mem_result, usm_dev_mem_result, 128);
  // check results
  for (size_t i = 0; i < 128; i++) {
    if (host_mem_result[i] != expected_result[i]) {
      std::cerr << "ERROR: usm_host_mem_result[" << i << "] = " << usm_host_mem_result[i] << " != expected_result[" << i << "] = " << expected_result[i] << std::endl;
      all_ok = false;
    }
  }

  // free memory
  fpga_executor.deallocate(usm_dev_mem_result);
  fpga_executor.deallocate(usm_dev_mem_data);
  fpga_executor.deallocate(usm_host_mem_result);
  fpga_executor.deallocate(usm_host_mem_data);
  cpu_executor.deallocate(host_mem_result);
  cpu_executor.deallocate(host_mem_data);
  cpu_executor.deallocate(expected_result);
  
  // done
  if (all_ok) {
    std::cout << "Everything worked fine!" << std::endl;
    return 0;
  } else {
    std::cout << "There were errors!" << std::endl;
    return 1;
  }
  
}