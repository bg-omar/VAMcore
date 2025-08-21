//
// Created by mr on 8/13/2025.
//
#include <sycl/sycl.hpp>
#include <iostream>

int main() {
  std::cout << "[host] SYCL platforms & devices:\n";
  for (const auto& P : sycl::platform::get_platforms()) {
    std::cout << "Platform: "
              << P.get_info<sycl::info::platform::name>() << "\n";
    for (const auto& D : P.get_devices()) {
      std::cout << "  - Device: "
                << D.get_info<sycl::info::device::name>()
                << " | is_gpu=" << D.is_gpu()
                << " | backend=" << (int)D.get_backend()
                << "\n";
    }
  }
  return 0;
}
