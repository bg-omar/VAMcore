import taichi as ti
import math

# ti.init(arch=ti.cuda) # or OpenGL for intel arc A770 rendering
ti.init(arch=ti.opengl) # or OpenGL for intel arc A770 rendering

res = 1024
num_particles = 3000
pixels = ti.Vector.field(3, dtype=ti.f32, shape=(res, res))
pos = ti.Vector.field(2, dtype=ti.f32, shape=num_particles)
vel = ti.Vector.field(2, dtype=ti.f32, shape=num_particles)

@ti.kernel
def init_particles():
    for i in range(num_particles):
        angle = 2 * math.pi * i / num_particles
        r = 0.3 + 0.1 * (i % 10) / 10.0
        pos[i] = ti.Vector([
            0.5 + r * ti.cos(angle),
            0.5 + r * ti.sin(angle)
        ])
        vel[i] = ti.Vector([0.0, 0.0])

@ti.func
def swirl_force(p, t):
    x, y = p - ti.Vector([0.5, 0.5])
    r2 = x * x + y * y + 1e-5
    r = ti.sqrt(r2)
    swirl = ti.Vector([-y, x]) * (0.25 / r)
    inward = -ti.Vector([x, y]) * (0.1 / r2)
    pulse = 0.03 * ti.sin(10 * r - 6 * t)
    return (swirl + inward) * (1 + pulse)

@ti.kernel
def update_particles(t: ti.f32):
    for i in pos:
        f = swirl_force(pos[i], t)
        vel[i] += f * 0.01
        vel[i] *= 0.98  # drag
        pos[i] += vel[i] * 0.01

        # Boundary wrap-around
        for j in ti.static(range(2)):
            if pos[i][j] < 0: pos[i][j] += 1
            if pos[i][j] > 1: pos[i][j] -= 1

@ti.kernel
def render(t: ti.f32):
    for i, j in pixels:
        uv = ti.Vector([i / res, j / res])
        f = swirl_force(uv, t)
        tension = ti.sqrt(f.norm())
        glow = 1.0 / (1.0 + 10 * ((uv - 0.5).norm() ** 2))
        hue = 0.5 + 0.5 * ti.sin(10 * (uv.norm() - t))
        pixels[i, j] = glow * ti.Vector([hue * tension, tension**2, hue**0.5])

gui = ti.GUI("🧠 VAM Swirlcore", res=(res, res))
init_particles()
t = 0.0

while gui.running:
    update_particles(t)
    render(t)

    # Draw particles
    gui.set_image(pixels)
    gui.circles(pos.to_numpy(), radius=1.5, color=0xFFFFFF)
    gui.show()
    t += 0.02
