import numpy as np
import matplotlib.pyplot as plt

def traveling_wave(x, t, A=1.0, k=2*np.pi, omega=2*np.pi):
    """ψ(x, t) = A * sin(kx - ωt)"""
    return A * np.sin(k * x - omega * t)

def standing_wave(x, t, A=1.0, k=2*np.pi, omega=2*np.pi):
    """ψ(x, t) = A * sin(kx) * cos(ωt)"""
    return A * np.sin(k * x) * np.cos(omega * t)

def sech(x):
    return 1 / np.cosh(x)

def fermi_dirac(E, mu=0.5, T=1.0, k_B=1.0):
    """F(E) = 1 / [exp((E - μ)/(kB T)) + 1]"""
    exponent = (E - mu) / (k_B * T)
    return 1 / (np.exp(exponent) + 1)

def plot_wave_snapshots():
    x = np.linspace(0, 2*np.pi, 500)
    times = [0, 0.25, 0.5, 0.75]

    plt.figure(figsize=(10, 6))
    for i, t in enumerate(times):
        y = traveling_wave(x, t)
        plt.plot(x, y, label=f't = {t}')
    plt.title("Traveling Wave Snapshots")
    plt.xlabel("x")
    plt.ylabel("ψ(x,t)")
    plt.legend()
    plt.grid()
    plt.show()

def plot_sech_and_distribution():
    x = np.linspace(-10, 10, 400)
    E = np.linspace(-1, 2, 400)

    plt.figure(figsize=(12, 4))

    plt.subplot(1, 2, 1)
    plt.plot(x, sech(x))
    plt.title("Hyperbolic Secant")
    plt.xlabel("x")
    plt.ylabel("sech(x)")

    plt.subplot(1, 2, 2)
    for T in [0.1, 0.5, 1.0]:
        plt.plot(E, fermi_dirac(E, mu=1.0, T=T), label=f"T = {T}")
    plt.title("Fermi–Dirac Distribution")
    plt.xlabel("E")
    plt.ylabel("f(E)")
    plt.legend()

    plt.tight_layout()
    plt.show()

def verify_wave_speed(k=2*np.pi, omega=2*np.pi):
    """Numerical estimate of v = ω / k"""
    return omega / k

if __name__ == "__main__":
    plot_wave_snapshots()
    plot_sech_and_distribution()

    v = verify_wave_speed()
    print("Wave speed v = ω / k =", v)
