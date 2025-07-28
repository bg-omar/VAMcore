//
// Created by mr on 7/18/2025.
//

#include "vorticity_transport.h"


namespace vam {

	Vec3 VorticityTransport::baroclinic_term(const Vec3& grad_rho, const Vec3& grad_p, double rho) {
		return {
				(grad_rho[1]*grad_p[2] - grad_rho[2]*grad_p[1]) / (rho*rho),
				(grad_rho[2]*grad_p[0] - grad_rho[0]*grad_p[2]) / (rho*rho),
				(grad_rho[0]*grad_p[1] - grad_rho[1]*grad_p[0]) / (rho*rho)
		};
	}

	Vec3 VorticityTransport::compute_rhs(const Vec3& omega, const std::array<Vec3, 3>& grad_u,
										 double div_u, const Vec3& grad_rho, const Vec3& grad_p, double rho) {
		Vec3 stretch = {
				omega[0]*grad_u[0][0] + omega[1]*grad_u[0][1] + omega[2]*grad_u[0][2],
				omega[0]*grad_u[1][0] + omega[1]*grad_u[1][1] + omega[2]*grad_u[1][2],
				omega[0]*grad_u[2][0] + omega[1]*grad_u[2][1] + omega[2]*grad_u[2][2]
		};

		Vec3 compress = {
				-div_u * omega[0],
				-div_u * omega[1],
				-div_u * omega[2]
		};

		Vec3 baroclinic = baroclinic_term(grad_rho, grad_p, rho);

		return {
				stretch[0] + compress[0] + baroclinic[0],
				stretch[1] + compress[1] + baroclinic[1],
				stretch[2] + compress[2] + baroclinic[2]
		};
	}

}
