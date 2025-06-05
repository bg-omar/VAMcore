#include "biot_savart.h"
#include <cmath>


namespace vam {

        Vec3 BiotSavart::velocity(const Vec3& r,
                                                          const std::vector<Vec3>& X,
                                                          const std::vector<Vec3>& T,
                                                          double Gamma)
        {
		Vec3 v{0.0, 0.0, 0.0};
		constexpr double coeff = 1.0 / (4.0 * M_PI);

		for (size_t i = 0; i < X.size(); ++i) {
			Vec3 dr{
					r[0] - X[i][0],
					r[1] - X[i][1],
					r[2] - X[i][2]
			};

			double norm_dr = std::sqrt(dr[0]*dr[0] + dr[1]*dr[1] + dr[2]*dr[2]);
			if (norm_dr > 1e-6) {
				Vec3 cross{
						T[i][1] * dr[2] - T[i][2] * dr[1],
						T[i][2] * dr[0] - T[i][0] * dr[2],
						T[i][0] * dr[1] - T[i][1] * dr[0]
				};

				double scale = Gamma / (norm_dr * norm_dr * norm_dr);
				v[0] += coeff * cross[0] * scale;
				v[1] += coeff * cross[1] * scale;
				v[2] += coeff * cross[2] * scale;
			}
		}

		return v;
	}

}
