"""
Example usage of Vorticity2D class
Compute vorticity: ω = ∂v/∂x - ∂u/∂y


% Definition of local circulation density (vorticity) in 2D
Let \(\mathbf{u} = (u, v)\). Then
\[
\bm{\omega} = \nabla \times \mathbf{u}
= \left[ \begin{matrix}
\frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}
\end{matrix} \right]
= \frac{\partial v}{\partial x} - \frac{\partial u}{\partial y}.
\]

\[
\oint_A \mathbf{u} \cdot d\mathbf{L} = \iint_A \omega\,dx\,dy.
\]

% Examples
% Rigid-body rotation:
u = -Ω\,y,\quad v = Ω\,x,\quad \omega = 2Ω.

% Couette flow:
u = Δ\,y,\quad v = 0,\quad \omega = -Δ.
"""

from vorticity import Vorticity2D
import numpy as np

# Sample velocity field on grid
nx, ny = 100, 100
x = np.linspace(0, 1, nx)
y = np.linspace(0, 1, ny)
X, Y = np.meshgrid(x, y, indexing='ij')
u = -2.0 * Y      # rigid rotation with Ω=1
v = 2.0 * X

omega = Vorticity2D.compute(u, v, dx=1/(nx-1), dy=1/(ny-1))
print("Max vorticity:", np.max(omega))  # expected ~2.0
