import numpy as np

'''\section*{Potential Flow and Irrotational Motion}

Als een snelheidspotentiaal $\phi$ dan sluit dit het bestaan van roterende beweging uit:
\[
\mathbf{u} = \nabla \phi \Rightarrow \nabla \times \mathbf{u} = \bm{0}
\]

\textbf{Boundary Condition:}
\[
\frac{\partial \phi}{\partial n} = 0 \quad \text{op impermeabele grens}
\]

\textbf{Green's Identity:}
\[
\iiint \left[ \left(\frac{\partial \phi}{\partial x}\right)^2 + 
              \left(\frac{\partial \phi}{\partial y}\right)^2 +
              \left(\frac{\partial \phi}{\partial z}\right)^2 \right] dx\,dy\,dz
= - \iint_{\partial V} \phi \frac{\partial \phi}{\partial n} \, dA
\]

If
\[
\int \frac{\partial \phi}{\partial n} \, dA = 0 \Rightarrow \text{left-hand side } = 0
\]

\textbf{Laplacian (only possible everywhere):}
\[
\frac{d^2 \phi}{dx^2} + \frac{d^2 \phi}{dy^2} + \frac{d^2 \phi}{dz^2} = 0
\]

\section*{Inviscid Flow in Cylindrical Coordinates}

\textbf{Momentum equations (r, θ, z):}
\[
\frac{\partial u}{\partial t} + u \frac{\partial u}{\partial r} + 
v \left( \frac{1}{r} \frac{\partial u}{\partial \theta} - \frac{v}{r} \right) +
w \frac{\partial u}{\partial z} = - \frac{1}{\rho} \frac{\partial p}{\partial r}
\]

\[
\frac{\partial v}{\partial t} + u \frac{\partial v}{\partial r} + 
v \left( \frac{1}{r} \frac{\partial v}{\partial \theta} + \frac{u}{r} \right) +
w \frac{\partial v}{\partial z} = - \frac{1}{\rho r} \frac{\partial p}{\partial \theta}
\]

\[
\frac{\partial w}{\partial t} + u \frac{\partial w}{\partial r} +
v \frac{1}{r} \frac{\partial w}{\partial \theta} +
w \frac{\partial w}{\partial z} = - \frac{1}{\rho} \frac{\partial p}{\partial z}
\]

\textbf{Simplified axisymmetric (no θ-dependence):}
\[
\frac{\partial u}{\partial t} + u \frac{\partial u}{\partial r} - \frac{v^2}{r} + w \frac{\partial u}{\partial z}
= - \frac{1}{\rho} \frac{\partial p}{\partial r}
\]

\[
\frac{\partial v}{\partial t} + u \frac{\partial v}{\partial r} + \frac{u v}{r} + w \frac{\partial v}{\partial z} = 0
\]

\[
\frac{\partial w}{\partial t} + u \frac{\partial w}{\partial r} + w \frac{\partial w}{\partial z}
= - \frac{1}{\rho} \frac{\partial p}{\partial z}
\]

\textbf{Integrated:}
\[
\int \frac{dp}{\rho} = - \nabla \phi + \int V^2 \, dr
\]
'''
import os
import sys

# Set path if needed
sys.path.insert(0, os.path.abspath("."))
def laplacian(phi, dx):
    """Compute 3D Laplacian assuming uniform spacing"""
    return (
            np.roll(phi, 1, axis=0) + np.roll(phi, -1, axis=0) +
            np.roll(phi, 1, axis=1) + np.roll(phi, -1, axis=1) +
            np.roll(phi, 1, axis=2) + np.roll(phi, -1, axis=2) -
            6 * phi
    ) / dx**2
