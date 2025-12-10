'''

\subsection*{1. Rossbygetal}

\[
    Ro = \frac{U}{2 \Omega d}
\]
\textit{Hoe kleiner het Rossbygetal, hoe sterker het rotatie-effect.}

\textit{Groter Coriolis-effect t.o.v. interne traagheid.}

\subsection*{2. Ekmangetal}

\[
    Ek = \frac{\nu_e}{\Omega H^2}
\]
\textit{Relatieve belangrijkheid van horizontale versus verticale wrijving.}

\vspace{1em}

\subsection*{3. Koppel en traagheidsmoment}

\[
\tau_{\text{torque}} = \text{Inertia} \times \text{Angular acceleration}
= I \alpha
\]

Voor een massieve cilinder met straal \( R \) en hoogte \( h \):

\[
    I = \frac{1}{2} \rho \pi R^2 h R^2 = \frac{1}{2} \rho \pi h R^4
\]

\[
\tau = \frac{1}{2} \rho \pi h R^4 \alpha
\]

\vspace{1em}

\subsection*{4. Massa van de cilinder}

\[
    m = \rho V = \rho \pi R^2 H
\]

\[
    I = \frac{m R^2}{2}
\]

'''
import os
import sys

# Set path if needed
sys.path.insert(0, os.path.abspath("."))
from swirl_string_core import rossby_number, ekman_number, cylinder_mass, cylinder_inertia, torque

U = 10.0       # velocity in m/s
omega = 7.29e-5  # Earth's rotation rad/s
d = 1e6        # depth in meters

Ro = rossby_number(U, omega, d)
print("Rossby number:", Ro)

nu = 1e-6     # viscosity in m²/s
H = 1000      # height

Ek = ekman_number(nu, omega, H)
print("Ekman number:", Ek)

rho = 1025     # density of seawater kg/m³
R = 2.0        # radius
H = 10.0       # height
alpha = 0.1    # angular acceleration

m = cylinder_mass(rho, R, H)
I = cylinder_inertia(m, R)
T = torque(I, alpha)

print("Mass:", m)
print("Moment of Inertia:", I)
print("Torque:", T)