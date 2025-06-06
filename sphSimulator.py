from pysph.base.kernels import CubicSpline
from pysph.base.utils import get_particle_array
from pysph.solver.application import Application
import numpy as np
from pysph.solver.solver import Solver
from pysph.sph.integrator import PECIntegrator

from pysph.sph.equation import Group, Equation
from pysph.sph.basic_equations import ContinuityEquation
from pysph.sph.integrator_step import WCSPHStep
from pysph.sph.wc.basic import MomentumEquation


# Dummy pressureless dynamics just to get motion from velocity
class NoOpEquation(Equation):
    def initialize(self, d_idx, d_au, d_av):
        d_au[d_idx] = 0.0
        d_av[d_idx] = 0.0


def initialize_vortex(x, y, strength=1.0):
    r_squared = x**2 + y**2 + 1e-12  # Avoid division by zero
    u = -strength * y / r_squared
    v = strength * x / r_squared
    return u, v

class VortexSimulation(Application):
    from pysph.base.kernels import CubicSpline  # or any other kernel you like

    def get_kernel(self):
        return CubicSpline(dim=2)

    def create_particles(self):
        # Grid of particles in 2D domain
        n = 50  # number of points per side
        dx = dy = 0.05
        x, y = np.meshgrid(
            np.linspace(-1, 1, n),
            np.linspace(-1, 1, n)
        )
        x = x.ravel()
        y = y.ravel()

        # Set velocities from vortex field
        u, v = initialize_vortex(x, y, strength=1.0)

        # Create particle array
        pa = get_particle_array(
            name='fluid',
            x=x, y=y, u=u, v=v,
            additional_props=[
                'arho', 'au', 'av', 'cs', 'dt_cfl', 'dt_force',
                'rho0', 'u0', 'v0', 'w0', 'x0', 'y0', 'z0',
                'ax', 'ay', 'az'
            ]

        )

        # Optionally add other properties like mass, density, smoothing length
        pa.m[:] = 1.0
        pa.h[:] = dx * 1.5
        pa.rho0[:] = pa.rho
        pa.u0[:] = pa.u
        pa.v0[:] = pa.v
        pa.w0[:] = 0.0
        pa.x0[:] = pa.x
        pa.y0[:] = pa.y
        pa.z0[:] = 0.0
        pa.ax[:] = 0.0
        pa.ay[:] = 0.0
        pa.az[:] = 0.0

        return [pa]

    def create_solver(self):
        kernel = self.get_kernel()
        integrator = PECIntegrator(fluid=WCSPHStep())

        solver = Solver(
            kernel=kernel,
            dim=2,
            integrator=integrator,
            dt=1e-3,
            tf=1.0
        )
        return solver


    def create_equations(self):
        return [Group(equations=[
            ContinuityEquation(dest='fluid', sources=['fluid']),
            MomentumEquation(dest='fluid', sources=['fluid'], c0=1.0, alpha=0.1, beta=0.0),
        ])]


if __name__ == '__main__':
    app = VortexSimulation()
    app.run()
