import numpy as np

"""
Note: This example shows a Python implementation. For C++ bindings, use:
    from swirl_string_core import rotating_frame_rhs, crocco_gradient
    # rotating_frame_rhs(velocity, vorticity, grad_phi, grad_p, omega, rho)
    # crocco_gradient(velocity, vorticity, grad_phi, grad_p, rho)

\section*{Relative Vorticity}

Newton's law in a rotating reference frame:
\[
\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}
= -2\bm{\Omega} \times \mathbf{u} - \nabla \phi - \frac{1}{\rho} \nabla p
\]

Expanded form:
\[
\frac{\partial \mathbf{u}}{\partial t}
+ \nabla \left( \frac{|\mathbf{u}|^2}{2} \right)
+ (\nabla \times \mathbf{u}) \times \mathbf{u}
= -2\bm{\Omega} \times \mathbf{u} - \nabla \phi - \frac{1}{\rho} \nabla p
\]

\section*{Crocco's Theorem (Incompressible, Inviscid)}

\begin{align*}
\nabla \times \mathbf{u} \times \mathbf{u}
= \frac{1}{\rho} \nabla \mathcal{H} \\
\text{where } \mathcal{H} = p + \frac{1}{2} \rho |\mathbf{v}|^2 + \rho \phi
\end{align*}

"""
def crocco_gradient(velocity, vorticity, rho, grad_phi, grad_p):
    """
    Compute total force per unit mass in Crocco's theorem.
    ∇(H) = ρ (du/dt + ∇(u²/2) + ω × u)
    """
    u = velocity
    omega_cross_u = np.cross(vorticity, velocity)
    kinetic_grad = 0.5 * np.gradient(np.linalg.norm(u)**2)
    pressure_term = -grad_p / rho
    potential_term = -grad_phi
    coriolis_term = omega_cross_u * 2
    return coriolis_term + kinetic_grad + pressure_term + potential_term