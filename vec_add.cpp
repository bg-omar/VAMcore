// icx -fsycl -O3 -I "C:\Program Files (x86)\Intel\oneAPI\compiler\latest\include" C:\workspace\projects\VAMcore\vec_add.cpp -o C:\workspace\projects\VAMcore\vec_add.exe
#include <sycl/sycl.hpp>
#include <iostream>
#include <vector>

int main() {
  sycl::queue q{ sycl::gpu_selector_v };

  const auto dev = q.get_device();
  const auto plt = dev.get_platform();
  std::cout << "Running on: "
            << dev.get_info<sycl::info::device::name>()
            << " (" << plt.get_info<sycl::info::platform::name>() << ")\n";

  constexpr size_t N = 16;
  std::vector<int> a(N), b(N), c(N);
  for (size_t i = 0; i < N; ++i) { a[i] = int(i); b[i] = int(2*i); }

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

  std::cout << "Results: ";
  for (size_t i = 0; i < N; ++i)
    std::cout << c[i] << (i + 1 < N ? ' ' : '\n');

  return 0;
}
