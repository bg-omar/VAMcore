import numpy as np
# Fluid dynamics computations:
#
# % Vorticity
# \text{Vorticity: } \bm{\omega} = \nabla \times \mathbf{v}
#
# % Divergence
# \text{Divergentie: } \operatorname{div} \, \mathbf{F} = \nabla \cdot \mathbf{F} = \frac{\partial F_x}{\partial x} + \frac{\partial F_y}{\partial y} + \frac{\partial F_z}{\partial z}
#
# % Circulatie
# \text{Circulatie: } \Gamma = \oint_{(c)} \mathbf{v} \cdot d\mathbf{l} = \iint_{(S)} (\nabla \times \mathbf{v}) \cdot \mathbf{dS} = \iint_{(S)} \bm{\omega} \cdot d\mathbf{A}
#
# % Kelvin
# \text{Circulatie stelling van Kelvin: } \frac{D\Gamma}{Dt} = 0
#
# % Enstrofie
# \text{Enstrofie: } \mathcal{E} = \iint_{S} \omega^2 \, ds

def compute_vorticity(grad_v):
    # grad_v: 3x3 velocity gradient tensor
    return np.array([
        grad_v[2,1] - grad_v[1,2],
        grad_v[0,2] - grad_v[2,0],
        grad_v[1,0] - grad_v[0,1]
    ])

def compute_divergence(F):
    # F: gradient field, shape (3, 3), diagonal elements are partial derivatives
    return F[0,0] + F[1,1] + F[2,2]

def circulation_line_integral(v_field, path_dl):
    # v_field: array of velocity vectors along path
    # path_dl: array of corresponding dl vectors along path
    return np.sum(np.einsum('ij,ij->i', v_field, path_dl))

def circulation_surface_integral(omega_field, dA_field):
    # omega_field, dA_field: array of vectors over surface
    return np.sum(np.einsum('ij,ij->i', omega_field, dA_field))

def enstrophy(omega_magnitude_squared, ds_area):
    # omega_magnitude_squared: array of ω^2 values over surface
    # ds_area: corresponding area elements
    return np.sum(omega_magnitude_squared * ds_area)
