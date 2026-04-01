// index.d.ts - TypeScript definitions for swirl-string-core

export type Vec3 = [number, number, number] | { x: number; y: number; z: number };
export type Vec3Array = Vec3[] | Float64Array;

export interface BiotSavartInvariants {
    hCharge: number;
    hMass: number;
    aMu: number;
}

export interface FrenetFrames {
    T: Float64Array;
    N: Float64Array;
    B: Float64Array;
}

export interface CurvatureTorsion {
    curvature: number[];
    torsion: number[];
}

/**
 * Biot-Savart module for computing velocity fields from vortex filaments
 */
export interface BiotSavartModule {
    /**
     * Compute velocity field from a closed curve at given grid points
     * @param curve Array of [x, y, z] points or Float64Array (flat, length = N*3)
     * @param gridPoints Array of [x, y, z] points or Float64Array (flat, length = M*3)
     * @returns Float64Array of velocities (flat, length = M*3)
     */
    computeVelocity(curve: Vec3Array, gridPoints: Vec3Array): Float64Array;

    /**
     * Compute vorticity from velocity field on a regular grid
     * @param velocity Velocity field as Float64Array (flat)
     * @param shape Grid shape [nx, ny, nz]
     * @param spacing Grid spacing
     * @returns Float64Array of vorticity (flat)
     */
    computeVorticity(velocity: Vec3Array, shape: [number, number, number], spacing: number): Float64Array;

    /**
     * Extract cubic interior field subset
     * @param field Field as Float64Array (flat)
     * @param shape Grid shape [nx, ny, nz]
     * @param margin Margin size
     * @returns Float64Array of interior field (flat)
     */
    extractInterior(field: Vec3Array, shape: [number, number, number], margin: number): Float64Array;

    /**
     * Compute invariants (H_charge, H_mass, a_mu)
     * @param vSub Velocity subset
     * @param wSub Vorticity subset
     * @param rSq Squared distances
     * @returns Object with hCharge, hMass, aMu
     */
    computeInvariants(vSub: Vec3Array, wSub: Vec3Array, rSq: number[]): BiotSavartInvariants;

    /**
     * Compute velocity at a single point due to a filament
     * @param r Point [x, y, z]
     * @param filamentPoints Filament points
     * @param tangentVectors Tangent vectors
     * @param circulation Circulation (default: 1.0)
     * @returns Velocity vector [vx, vy, vz]
     */
    biotSavartVelocity(r: Vec3, filamentPoints: Vec3Array, tangentVectors: Vec3Array, circulation?: number): Vec3;

    /**
     * Compute velocity at grid points for a polyline
     * @param polyline Polyline points
     * @param grid Grid points
     * @returns Float64Array of velocities (flat, length = grid.length*3)
     */
    biotSavartVelocityGrid(polyline: Vec3Array, grid: Vec3Array): Float64Array;
}

/**
 * Fluid dynamics module
 */
export interface FluidDynamicsModule {
    /**
     * Compute Bernoulli pressure field from velocity magnitude
     */
    computePressureField(velocityMagnitude: number[], rhoAe: number, pInfinity: number): number[];

    /**
     * Compute velocity magnitude from vector field
     */
    computeVelocityMagnitude(velocity: Vec3Array): number[];

    /**
     * Euler-step update of particle positions
     * @returns Updated positions
     */
    evolvePositionsEuler(positions: Vec3Array, velocity: Vec3Array, dt: number): Float64Array;

    /**
     * Compute helicity H = ∫ v · ω dV over a discretized field (with volume element)
     */
    computeHelicityField(velocity: Vec3Array, vorticity: Vec3Array, dV: number): number;

    /**
     * Swirl clock rate: 0.5 * (dv/dx - du/dy)
     */
    swirlClockRate(dvDx: number, duDy: number): number;

    /**
     * Compute kinetic energy E = (1/2) * ρ * ∑ |v|^2
     */
    computeKineticEnergy(velocity: Vec3Array, rhoAe: number): number;
}

/**
 * Frenet helicity module
 */
export interface FrenetHelicityModule {
    /**
     * Compute Frenet frames (T, N, B) from 3D filament points
     */
    computeFrenetFrames(X: Vec3Array): FrenetFrames;

    /**
     * Compute curvature and torsion from tangent and normal vectors
     */
    computeCurvatureTorsion(T: Vec3Array, N: Vec3Array): CurvatureTorsion;

    /**
     * Compute helicity H = ∫ v · ω dV
     */
    computeHelicity(velocity: Vec3Array, vorticity: Vec3Array): number;

    /**
     * Evolve vortex knot filaments using Biot-Savart dynamics
     */
    evolveVortexKnot(positions: Vec3Array, tangents: Vec3Array, dt: number, gamma?: number): Float64Array;

    /**
     * Runge-Kutta 4th order time integrator
     */
    rk4Integrate(positions: Vec3Array, tangents: Vec3Array, dt: number, gamma?: number): Float64Array;
}

/**
 * Main module interface
 */
export interface SwirlStringCore {
    version: string;
    isAvailable: boolean;
    isNative: boolean;
    isWasm: boolean;
    error?: string;

    // Biot-Savart functions
    computeVelocity: BiotSavartModule['computeVelocity'];
    computeVorticity: BiotSavartModule['computeVorticity'];
    extractInterior: BiotSavartModule['extractInterior'];
    computeInvariants: BiotSavartModule['computeInvariants'];
    biotSavartVelocity: BiotSavartModule['biotSavartVelocity'];
    biotSavartVelocityGrid: BiotSavartModule['biotSavartVelocityGrid'];

    // Fluid dynamics functions
    computePressureField: FluidDynamicsModule['computePressureField'];
    computeVelocityMagnitude: FluidDynamicsModule['computeVelocityMagnitude'];
    evolvePositionsEuler: FluidDynamicsModule['evolvePositionsEuler'];
    computeHelicityField: FluidDynamicsModule['computeHelicityField'];
    swirlClockRate: FluidDynamicsModule['swirlClockRate'];
    computeKineticEnergy: FluidDynamicsModule['computeKineticEnergy'];

    // Frenet helicity functions
    computeFrenetFrames: FrenetHelicityModule['computeFrenetFrames'];
    computeCurvatureTorsion: FrenetHelicityModule['computeCurvatureTorsion'];
    computeHelicity: FrenetHelicityModule['computeHelicity'];
    evolveVortexKnot: FrenetHelicityModule['evolveVortexKnot'];
    rk4Integrate: FrenetHelicityModule['rk4Integrate'];

    // Placeholder flags for modules not yet implemented
    fieldKernelsAvailable?: boolean;
    fieldOpsAvailable?: boolean;
    knotAvailable?: boolean;
    timeFieldAvailable?: boolean;
    hyperbolicVolumeAvailable?: boolean;
    radiationFlowAvailable?: boolean;
    swirlFieldAvailable?: boolean;
    thermoDynamicsAvailable?: boolean;
    timeEvolutionAvailable?: boolean;
    vortexRingAvailable?: boolean;
    vorticityDynamicsAvailable?: boolean;
    sstGravityAvailable?: boolean;
    sstExtensionsAvailable?: boolean;
}

declare const swirlStringCore: SwirlStringCore;
export default swirlStringCore;