# swirl-string-core npm Package

This package provides Node.js and WebAssembly bindings for the Swirl String Theory Core library, making it available for Angular and other JavaScript/TypeScript applications.

## Installation

```bash
npm install swirl-string-core
```

## Usage

### Node.js (Native Addon)

The package automatically detects the environment and loads the appropriate module:

```javascript
const sst = require('swirl-string-core');

// Check if module is available
if (!sst.isAvailable) {
    console.error('Module not available:', sst.error);
    return;
}

// Use Biot-Savart functions
const curve = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]];
const gridPoints = [[0.5, 0.5, 0.5]];
const velocities = sst.computeVelocity(curve, gridPoints);

console.log('Velocities:', velocities);
```

### Browser (WebAssembly)

In an Angular application:

```typescript
import * as sst from 'swirl-string-core';

// The module will automatically load the WASM version in the browser
const velocities = sst.computeVelocity(curve, gridPoints);
```

### TypeScript

Full TypeScript definitions are included:

```typescript
import sst, { Vec3, BiotSavartInvariants } from 'swirl-string-core';

const curve: Vec3[] = [[0, 0, 0], [1, 0, 0], [1, 1, 0]];
const grid: Vec3[] = [[0.5, 0.5, 0.5]];

const velocities: Float64Array = sst.computeVelocity(curve, grid);
```

## API Reference

### Biot-Savart Module

- `computeVelocity(curve, gridPoints)` - Compute velocity field from a closed curve
- `computeVorticity(velocity, shape, spacing)` - Compute vorticity from velocity field
- `extractInterior(field, shape, margin)` - Extract interior field subset
- `computeInvariants(vSub, wSub, rSq)` - Compute invariants (H_charge, H_mass, a_mu)
- `biotSavartVelocity(r, filamentPoints, tangentVectors, circulation?)` - Velocity at single point
- `biotSavartVelocityGrid(polyline, grid)` - Velocity at grid points

### Fluid Dynamics Module

- `computePressureField(velocityMagnitude, rhoAe, pInfinity)` - Bernoulli pressure field
- `computeVelocityMagnitude(velocity)` - Velocity magnitude from vector field
- `evolvePositionsEuler(positions, velocity, dt)` - Euler-step position update
- `computeHelicity(velocity, vorticity, dV)` - Compute helicity
- `swirlClockRate(dvDx, duDy)` - Swirl clock rate
- `computeKineticEnergy(velocity, rhoAe)` - Kinetic energy

### Frenet Helicity Module

- `computeFrenetFrames(X)` - Compute Frenet frames (T, N, B)
- `computeCurvatureTorsion(T, N)` - Compute curvature and torsion
- `computeHelicity(velocity, vorticity)` - Compute helicity
- `evolveVortexKnot(positions, tangents, dt, gamma?)` - Evolve vortex knot
- `rk4Integrate(positions, tangents, dt, gamma?)` - Runge-Kutta 4th order integrator

## Building from Source

### Prerequisites

- Node.js 14+
- CMake 3.23+
- C++ compiler (GCC, Clang, or MSVC)
- For WASM: Emscripten SDK

### Build Native Addon

```bash
npm install
npm run build:node
```

### Build WASM

```bash
# Install Emscripten SDK first
npm run build:wasm
```

### Build Both

```bash
npm run build:all
```

## Automated Publishing

This package uses GitHub Actions for automated building and publishing:

- **Test workflow**: Runs on every push/PR to test on multiple platforms
- **Publish workflow**: Automatically publishes to npm when you create a release or push a version tag (e.g., `v0.1.3`)

See [SETUP_NPM_PUBLISHING.md](docs/SETUP_NPM_PUBLISHING.md) for detailed setup instructions.

## Platform Support

- **Node.js**: Windows, Linux, macOS (native addon)
- **Browser**: All modern browsers (WebAssembly)

## License

CC BY-NC 4.0 (Non-Commercial)

## See Also

- [Python Package](https://pypi.org/project/swirl-string-core/)
- [GitHub Repository](https://github.com/Swirl-String-Theory/SSTcore)

