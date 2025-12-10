import numpy as np

"""
Note: This example shows a Python implementation. For C++ bindings, use:
    from swirl_string_core import baroclinic_term, compute_vorticity_rhs
    # baroclinic_term(grad_rho, grad_p, rho)
    # compute_vorticity_rhs(omega, grad_u, div_u, grad_rho, grad_p, rho)

\section*{Vorticity Transport Equation (Variable Density)}

\textbf{Condition:}
\textit{For a steady flow, the direction of velocity $\mathbf{u}$ and the gradient of density $\nabla \rho$ must be orthogonal.}

\textbf{Vorticity:} $\bm{\omega} = \nabla \times \mathbf{u}$

\textbf{Transport Equation:}
\[
\frac{D \bm{\omega}}{Dt}
= (\bm{\omega} \cdot \nabla)\mathbf{u} 
- (\nabla \cdot \mathbf{u}) \bm{\omega} 
+ \frac{1}{\rho^2} \nabla \rho \times \nabla p 
+ \nabla \times \mathbf{B}
\]

\textbf{Terms:}
\begin{itemize}
  \item Unsteady term: $\frac{\partial \bm{\omega}}{\partial t}$
  \item Vortex stretching: $(\bm{\omega} \cdot \nabla)\mathbf{u}$
  \item Baroclinic torque: $\frac{1}{\rho^2} \nabla \rho \times \nabla p$
  \item Viscous source: $\nabla \times \left( \frac{1}{\rho} \nabla \cdot \bm{\tau} \right )$
\end{itemize}

"""
def compute_baroclinic_term(grad_rho, grad_p, rho):
    """Compute baroclinic torque: (1/ρ²) ∇ρ × ∇p"""
    return np.cross(grad_rho, grad_p) / (rho ** 2)

def compute_vorticity_transport(omega, grad_u, div_u, grad_rho, grad_p, rho):
    """Compute RHS of vorticity transport equation"""
    stretch = omega @ grad_u  # vortex stretching
    compress = -div_u * omega
    baroclinic = compute_baroclinic_term(grad_rho, grad_p, rho)
    return stretch + compress + baroclinic  # viscous term neglected