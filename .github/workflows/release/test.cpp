#include <tsl/tsl.hpp>
#include <iostream>

int main() {
  std::cout << tsl::type_name<int>() << std::endl;
  return 0;
}