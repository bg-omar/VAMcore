import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Needed for 3D plotting
import spherogram
import matplotlib
matplotlib.use('TkAgg')  # Ensure it uses Tkinter backend
import os
script_name = os.path.splitext(os.path.basename(__file__))[0]

# Fourier coefficients for 6_2 knot (N=10)
a_x = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
b_x = np.array([-0.008900, 0.0, -0.153498, 0.0, -0.154080, 0.0, 0.032799, 0.0, -0.015252, 0.0])
a_y = np.array([-0.106450, 0.0, -0.061067, 0.0, -0.098726, 0.0, 0.036572, 0.0, 0.000187, 0.0])
b_y = np.zeros(10)
a_z = np.zeros(10)
b_z = np.array([0.0, 0.144705, 0.0, 0.069024, 0.0, -0.073844, 0.0, 0.002462, 0.0, -0.007937])

def knot_6_2(s):
    x = np.zeros_like(s)
    y = np.zeros_like(s)
    z = np.zeros_like(s)
    for j in range(10):
        x += a_x[j] * np.cos((j+1)*s) + b_x[j] * np.sin((j+1)*s)
        y += a_y[j] * np.cos((j+1)*s) + b_y[j] * np.sin((j+1)*s)
        z += a_z[j] * np.cos((j+1)*s) + b_z[j] * np.sin((j+1)*s)
    return x, y, z

# Parameter s from 0 to 2pi
s = np.linspace(0, 2*np.pi, 1000)
x, y, z = knot_6_2(s)

# # Plot the knot in 3D
# fig = plt.figure(figsize=(8,6))
# ax = fig.add_subplot(111, projection='3d')
# ax.plot(x, y, z, color='navy', linewidth=2)
# ax.set_xlabel('x')
# ax.set_ylabel('y')
# ax.set_zlabel('z')
# ax.set_title('6_2 Knot (Fourier Parameterization)')
# ax.grid(False)
# plt.tight_layout()




# Paste your coordinates here as a multi-line string
coord_text = """
-0.038785   -2.791829    0.038165
-0.154095   -2.769817    0.151242
-0.265682   -2.722181    0.259260
-0.370907   -2.650644    0.358577
-0.467377   -2.557734    0.445805
-0.553021   -2.446619    0.517915
-0.626166   -2.320910    0.572332
-0.685581   -2.184439    0.607040
-0.730495   -2.041035    0.620657
-0.760598   -1.894317    0.612515
-0.776009   -1.747513    0.582706
-0.777237   -1.603323    0.532119
-0.758270   -1.418647    0.435368
-0.718158   -1.245417    0.310848
-0.642808   -1.046720    0.128837
-0.522956   -0.832920   -0.102067
-0.404142   -0.671501   -0.279605
-0.271520   -0.521319   -0.421488
-0.156547   -0.407199   -0.497661
-0.065293   -0.324419   -0.528780
0.030298   -0.243728   -0.535864
0.130277   -0.164915   -0.518474
0.270367   -0.062360   -0.458496
0.417761    0.038069   -0.360769
0.649680    0.188002   -0.160568
1.003536    0.428432    0.187948
1.187603    0.582137    0.362652
1.319198    0.720751    0.473873
1.404877    0.835095    0.534920
1.476707    0.958501    0.573913
1.532481    1.090386    0.589340
1.570310    1.229432    0.580741
1.588728    1.373573    0.548705
1.586774    1.520046    0.494817
1.564056    1.665505    0.421554
1.520785    1.806178    0.332157
1.457780    1.938088    0.230455
1.376441    2.057279    0.120686
1.278691    2.160073    0.007300
1.166893    2.243307   -0.105233
1.043742    2.304549   -0.212609
0.912135    2.342261   -0.310849
0.775044    2.355911   -0.396445
0.635372    2.346008   -0.466468
0.495822    2.314064   -0.518647
0.358781    2.262493   -0.551419
0.226218    2.194432   -0.563948
0.099611    2.113523   -0.556117
-0.058370    1.992388   -0.515067
-0.203384    1.864373   -0.441942
-0.336253    1.737381   -0.341473
-0.488580    1.588792   -0.186778
-0.687034    1.408045    0.058928
-0.912221    1.230287    0.333347
-1.058875    1.118853    0.476504
-1.179641    1.020111    0.565261
-1.301428    0.907136    0.625840
-1.420821    0.776232    0.654864
-1.533244    0.625713    0.650552
-1.633378    0.456096    0.612831
-1.715674    0.269984    0.543375
-1.774916    0.071672    0.445552
-1.806752   -0.133421    0.324286
-1.808161   -0.339423    0.185821
-1.777780   -0.540666    0.037405
-1.716077   -0.732227   -0.113097
-1.625337   -0.910305   -0.257629
-1.509462   -1.072392   -0.388401
-1.373620   -1.217240   -0.498331
-1.223760   -1.344668   -0.581443
-1.066061   -1.455255   -0.633213
-0.906367   -1.550006   -0.650821
-0.749665   -1.630029   -0.633307
-0.599669   -1.696303   -0.581621
-0.458545   -1.749536   -0.498564
-0.326813   -1.790134   -0.388631
-0.173636   -1.823333   -0.222575
0.000000   -1.837419    0.000000
0.173635   -1.823333    0.222575
0.326812   -1.790133    0.388630
0.458544   -1.749537    0.498564
0.599668   -1.696304    0.581621
0.749664   -1.630030    0.633307
0.906366   -1.550006    0.650821
1.066060   -1.455256    0.633213
1.223759   -1.344668    0.581444
1.373619   -1.217241    0.498332
1.509461   -1.072393    0.388402
1.625336   -0.910306    0.257629
1.716077   -0.732228    0.113098
1.777780   -0.540667   -0.037404
1.808161   -0.339424   -0.185820
1.806753   -0.133422   -0.324286
1.774916    0.071671   -0.445552
1.715674    0.269982   -0.543375
1.633378    0.456096   -0.612831
1.533245    0.625712   -0.650552
1.420822    0.776231   -0.654864
1.301429    0.907135   -0.625840
1.179642    1.020111   -0.565262
1.058876    1.118853   -0.476505
0.912222    1.230286   -0.333347
0.631223    1.456460    0.012750
0.459098    1.617291    0.219730
0.304078    1.768670    0.368841
0.168327    1.896560    0.462997
0.020091    2.023658    0.528487
-0.141081    2.141682    0.560968
-0.269805    2.218733    0.562043
-0.404050    2.281682    0.542718
-0.542169    2.327029    0.503348
-0.682042    2.351852    0.445013
-0.821167    2.354025    0.369513
-0.956759    2.332359    0.279346
-1.085877    2.286693    0.177644
-1.205559    2.217903    0.068088
-1.312959    2.127839   -0.045219
-1.405481    2.019198   -0.157899
-1.480899    1.895341   -0.265467
-1.537454    1.760064   -0.363522
-1.573935    1.617358   -0.447941
-1.589725    1.471160   -0.515071
-1.584816    1.325118   -0.561910
-1.559795    1.182401   -0.586262
-1.515798    1.045548   -0.586866
-1.454444    0.916380   -0.563481
-1.377740    0.795966   -0.516917
-1.287974    0.684651   -0.449030
-1.152224    0.549793   -0.330367
-0.965013    0.399850   -0.149891
-0.571268    0.137776    0.232824
-0.380279    0.013097    0.388375
-0.234632   -0.087760    0.477260
-0.096463   -0.190989    0.526972
0.002050   -0.270405    0.536222
0.096189   -0.351767    0.521026
0.214992   -0.463678    0.464256
0.326095   -0.580261    0.370217
0.453461   -0.734518    0.211764
0.586388   -0.936720   -0.013041
0.675977   -1.123818   -0.204111
0.730009   -1.287552   -0.344164
0.765104   -1.463831   -0.462436
0.777237   -1.603322   -0.532119
0.776009   -1.747511   -0.582706
0.760598   -1.894316   -0.612514
0.730496   -2.041034   -0.620657
0.685582   -2.184438   -0.607040
0.626167   -2.320909   -0.572333
0.553021   -2.446618   -0.517915
0.467377   -2.557733   -0.445806
0.370908   -2.650644   -0.358577
0.265682   -2.722181   -0.259260
0.154096   -2.769817   -0.151243
0.038786   -2.791828   -0.038166
0.000001   -2.793304   -0.000001
"""

# Parse the coordinates into a numpy array
coords = np.array([
    [float(num) for num in line.split()]
    for line in coord_text.strip().splitlines()
])

x, y, z = coords[:, 0], coords[:, 1], coords[:, 2]
#
# # 3D plot
# fig = plt.figure(figsize=(8, 6))
# ax = fig.add_subplot(111, projection='3d')
# ax.plot(x, y, z, '-', lw=2, color='darkorange')
# ax.scatter([x[0]], [y[0]], [z[0]], color='red', label='Start')
# ax.scatter([x[-1]], [y[-1]], [z[-1]], color='blue', label='End')
# ax.set_xlabel('x')
# ax.set_ylabel('y')
# ax.set_zlabel('z')
# ax.set_title('6₍₂₎ Knot (Coordinate Data)')
# ax.legend()
# plt.tight_layout()
#


# Coefficient arrays (j runs from 1 to 10)
a_x2 = np.array([0.101500,  0.000000, -0.058576, 0.000000, 0.010809, 0.000000, -0.019292, 0.000000, 0.021062, 0.000000])
b_x2 = np.array([0.063367,  0.000000, -0.047834, 0.000000, -0.123037, 0.000000, 0.002397, 0.000000, -0.027679, 0.000000])

a_y2 = np.array([0.000000, -0.360746, 0.000000, 0.008628, 0.000000, -0.044936, 0.000000, -0.003736, 0.000000, -0.001866])
b_y2 = np.array([0.000000, -0.006923, 0.000000, -0.021589, 0.000000, 0.021844, 0.000000, -0.004946, 0.000000, 0.020238])

a_z2 = np.array([0.018163,  0.000000, 0.050709, 0.000000, 0.101439, 0.000000, -0.040565, 0.000000, -0.001380, 0.000000])
b_z2 = np.array([-0.016010, 0.000000, -0.083507, 0.000000, -0.013338, 0.000000, -0.010632, 0.000000, 0.021509, 0.000000])

def knot_6_2p(s):
    x = np.zeros_like(s)
    y = np.zeros_like(s)
    z = np.zeros_like(s)
    for j in range(10):
        x += a_x2[j] * np.cos((j+1)*s) + b_x2[j] * np.sin((j+1)*s)
        y += a_y2[j] * np.cos((j+1)*s) + b_y2[j] * np.sin((j+1)*s)
        z += a_z2[j] * np.cos((j+1)*s) + b_z2[j] * np.sin((j+1)*s)
    return x, y, z


def knot_6_2p_tangent(s):
    # Derivative with respect to s
    dx = np.zeros_like(s)
    dy = np.zeros_like(s)
    dz = np.zeros_like(s)
    for j in range(10):
        n = j + 1
        dx += -n * a_x[j] * np.sin(n * s) + n * b_x[j] * np.cos(n * s)
        dy += -n * a_y[j] * np.sin(n * s) + n * b_y[j] * np.cos(n * s)
        dz += -n * a_z[j] * np.sin(n * s) + n * b_z[j] * np.cos(n * s)
    return dx, dy, dz

s = np.linspace(0, 2*np.pi, 1000)
x, y, z = knot_6_2p(s)
dx, dy, dz = knot_6_2p_tangent(s)

# # Plot knot and tangent vectors
# fig = plt.figure(figsize=(9, 7))
# ax = fig.add_subplot(111, projection='3d')
# ax.plot(x, y, z, color='slateblue', lw=2, label='Knot centerline')
#
# # Show tangent vectors every N points
# N = 50
# ax.quiver(x[::N], y[::N], z[::N],
#           dx[::N], dy[::N], dz[::N],
#           length=0.2, normalize=True, color='crimson', linewidth=1)
#
# ax.set_xlabel('x')
# ax.set_ylabel('y')
# ax.set_zlabel('z')
# ax.set_title(r'$6_2$ Knot with Tangent Vectors')
# plt.tight_layout()


from matplotlib import cm

# Compute unit tangent and curvature
T = np.vstack((dx, dy, dz)).T
T_norm = T / np.linalg.norm(T, axis=1)[:, None]
dT_ds = np.gradient(T_norm, axis=0)
curvature = np.linalg.norm(dT_ds, axis=1)

# Normalize for colormap
norm = plt.Normalize(curvature.min(), curvature.max())
colors = cm.viridis(norm(curvature))

# fig = plt.figure(figsize=(9, 7))
# ax = fig.add_subplot(111, projection='3d')
#
# for i in range(len(x)-1):
#     ax.plot(x[i:i+2], y[i:i+2], z[i:i+2], color=colors[i])
#
# ax.set_title(r'$6_2$ Knot Colored by Local Curvature (Vorticity Proxy)')
# ax.set_xlabel('x')
# ax.set_ylabel('y')
# ax.set_zlabel('z')
# plt.tight_layout()
# plt.show()

# New figure with neon effect
fig = plt.figure(figsize=(12, 10), facecolor='black')
ax = fig.add_subplot(111, projection='3d', facecolor='black')

# Apply "neon glow" by layering lines with decreasing alpha and increasing width
# Boost glow by adding more layers
for glow in range(15, 0, -1):  # More layers = stronger glow
    alpha = 0.01 * glow**1.3   # Exponential alpha for better blending
    linewidth = 1 + glow / 2
    ax.plot(x, y, z, color=(0.0, 1.0, 1.0, alpha), linewidth=linewidth)

for i in range(0, len(x), 5):
    size = 8
    alpha = 0.2 + 0.6 * (i / len(x))
    ax.scatter([x[i]], [y[i]], [z[i]], s=size, color='cyan', alpha=alpha)


# Final main line on top
ax.plot(x, y, z, color=(0.0, 1.0, 1.0, 1.0), linewidth=1.5)

# Add "æther haze" via faint scatter
ax.scatter(x[::20], y[::20], z[::20], s=1, c='cyan', alpha=0.02)
ax.scatter(x[::10], y[::10], z[::10], c='cyan', alpha=0.01, s=5)
r = np.sqrt(x**2 + y**2 + z**2)
fog_alpha = 0.01 + 0.03 * (r - r.min()) / (r.max() - r.min())
ax.scatter(x, y, z, c='cyan', alpha=fog_alpha, s=2)

# Turn off axes, grid, and ticks
ax.set_axis_off()

plt.tight_layout()
plt.savefig("glowing_knot.png", dpi=300, transparent=True)

plt.show()


import numpy as np
import pyvista as pv
from pyvista import themes

# Fourier coefficients (second set as in your script)
a_x2 = np.array([0.101500,  0, -0.058576, 0, 0.010809, 0, -0.019292, 0, 0.021062, 0])
b_x2 = np.array([0.063367,  0, -0.047834, 0, -0.123037, 0, 0.002397, 0, -0.027679, 0])
a_y2 = np.array([0, -0.360746, 0, 0.008628, 0, -0.044936, 0, -0.003736, 0, -0.001866])
b_y2 = np.array([0, -0.006923, 0, -0.021589, 0, 0.021844, 0, -0.004946, 0, 0.020238])
a_z2 = np.array([0.018163, 0, 0.050709, 0, 0.101439, 0, -0.040565, 0, -0.001380, 0])
b_z2 = np.array([-0.016010, 0, -0.083507, 0, -0.013338, 0, -0.010632, 0, 0.021509, 0])

def knot(s, ax, bx, ay, by, az, bz):
    x = y = z = np.zeros_like(s)
    for j in range(len(ax)):
        n = j + 1
        x += ax[j] * np.cos(n*s) + bx[j] * np.sin(n*s)
        y += ay[j] * np.cos(n*s) + by[j] * np.sin(n*s)
        z += az[j] * np.cos(n*s) + bz[j] * np.sin(n*s)
    return x, y, z

# Sample the knot
s = np.linspace(0, 2*np.pi, 2000)
x, y, z = knot(s, a_x2, b_x2, a_y2, b_y2, a_z2, b_z2)

# Create a tube mesh around the centerline
points = np.vstack((x, y, z)).T
line = pv.Spline(points, 2000)
tube = line.tube(radius=0.03, n_sides=50)

# Set up plotter with cinematic theme
plotter = pv.Plotter(window_size=(1200, 900))
plotter.set_background('black')
theme = themes.DocumentTheme()
theme.lighting = True
plotter.theme = theme

# Add tube with emissive (glow) material
plotter.add_mesh(tube, color=(0, 255, 255), specular=1.0,
                 smooth_shading=True, emissive=0.6)

plotter.enable_ssao(radius=1.5, bias=0.05, kernel_size=256, blur=True)
plotter.enable_anti_aliasing('ssaa')

# Add soft point lights for bloom effect
plotter.add_light(pv.Light(position=(2,2,2), color=(0.2,1,1), intensity=2))
plotter.add_light(pv.Light(position=(-2,-1,0.5), color=(0.2,1,1), intensity=1.5))


# Render with bloom-like tone mapping
plotter.show(auto_close=False)
plotter.camera_position = 'iso'  # Isometric view
plotter.show(screenshot='knot_pyvista.png')
