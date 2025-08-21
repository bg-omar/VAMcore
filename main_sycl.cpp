//
// Created by mr on 8/13/2025.
//
#include <sycl/sycl.hpp>
#include <iostream>
#include <vector>

int main() {
  std::cout << "[host] enumerate devices\n";
  sycl::device dev;
  bool found = false;
  for (const auto& P : sycl::platform::get_platforms()) {
    for (const auto& D : P.get_devices()) {
      if (D.is_gpu()) { dev = D; found = true; break; }
    }
    if (found) break;
  }
  if (!found) {
    std::cout << "[host] no GPU visible; using default device\n";
    dev = sycl::device{sycl::default_selector_v};
  }

  std::cout << "[host] picked: "
            << dev.get_info<sycl::info::device::name>() << "\n";
  sycl::queue q{dev};

  constexpr size_t N = 16;
  std::vector<int> a(N), b(N), c(N);
  for (size_t i = 0; i < N; ++i) { a[i] = int(i); b[i] = int(2 * i); }

  {
    sycl::buffer A(a.data(), sycl::range<1>(N));
    sycl::buffer B(b.data(), sycl::range<1>(N));
    sycl::buffer C(c.data(), sycl::range<1>(N));
    q.submit([&](sycl::handler& h) {
      sycl::accessor accA(A, h, sycl::read_only);
      sycl::accessor accB(B, h, sycl::read_only);
      sycl::accessor accC(C, h, sycl::write_only, sycl::no_init);
      h.parallel_for(sycl::range<1>(N), [=](sycl::id<1> i) {
        accC[i] = accA[i] + accB[i];
      });
    });
    q.wait();
  }

  std::cout << "[host] results: ";
  for (size_t i = 0; i < N; ++i) std::cout << c[i] << (i + 1 < N ? ' ' : '\n');
  return 0;
}
