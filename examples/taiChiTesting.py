import os

import taichi as ti
ti.init(arch=ti.opengl)

import numpy as np
from swirl_string_core import compute_swirl_field
res = 512
field = compute_swirl_field(res, time=0.5)

arr = np.array(field).reshape((res, res, 2)).astype(np.float32)
ti_field = ti.Vector.ndarray(2, ti.f32, shape=(res, res))
ti_field.from_numpy(arr)

print("Sample force at center:", ti_field[res//2, res//2])