import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import os
import sys

# Set path if needed
sys.path.insert(0, os.path.abspath("."))
from swirl_string_core import RadiationFlow, radiation_force, van_der_pol_dx, van_der_pol_dy

# Radiation force example
F = radiation_force(I0=1000, Qm=1.2, lambda1=600e-9, lambda2=500e-9, lambda_g=550e-9)
print("Radiation force (N):", F)

# Van der Pol oscillator simulation
def vdp(t, y, mu):
    x, v = y
    return [van_der_pol_dx(x, v), van_der_pol_dy(x, v, mu)]

mu = 2.0
sol = solve_ivp(vdp, [0, 20], [2, 0], args=(mu,), dense_output=True)

t = np.linspace(0, 20, 500)
x, v = sol.sol(t)

plt.plot(x, v)
plt.title("Van der Pol Phase Space")
plt.xlabel("x")
plt.ylabel("dx/dt")
plt.grid(True)
plt.show()