import numpy as np

class BraidTo3D:
    """
    Translates an Artin Braid Word into a 3D vortex filament coordinate array
    based on Alexander's Theorem.
    """
    @staticmethod
    def generate_filaments(braid_word, num_strands=None, resolution_per_cross=50):
        if num_strands is None:
            num_strands = max([abs(c) for c in braid_word]) + 1 if braid_word else 1

        # Initialize logical strands at X = 0, 1, ... n-1
        strands = [[(float(i), 0.0, 0.0)] for i in range(num_strands)]

        # Track which physical position (x) currently holds which logical strand
        current_pos = {i: i for i in range(num_strands)}
        pos_to_strand = {i: i for i in range(num_strands)}

        z_current = 0.0
        dz = 2.0  # Z-distance per crossing

        # 1. Weave the braid
        for crossing in braid_word:
            pos_idx = abs(crossing) - 1
            sign = 1 if crossing > 0 else -1

            s1 = pos_to_strand[pos_idx]
            s2 = pos_to_strand[pos_idx + 1]

            for step in range(1, resolution_per_cross + 1):
                t = step / float(resolution_per_cross)
                z = z_current + t * dz

                # Strand 1 moves from pos_idx to pos_idx + 1
                x1 = pos_idx + t
                y1 = sign * 0.5 * np.sin(t * np.pi)
                strands[s1].append((x1, y1, z))

                # Strand 2 moves from pos_idx + 1 to pos_idx
                x2 = pos_idx + 1 - t
                y2 = -sign * 0.5 * np.sin(t * np.pi)
                strands[s2].append((x2, y2, z))

                # Other strands go straight
                for p in range(num_strands):
                    if p != pos_idx and p != pos_idx + 1:
                        s_other = pos_to_strand[p]
                        strands[s_other].append((float(p), 0.0, z))

            # Update permutations
            current_pos[s1] = pos_idx + 1
            current_pos[s2] = pos_idx
            pos_to_strand[pos_idx] = s2
            pos_to_strand[pos_idx + 1] = s1

            z_current += dz

        # 2. Trace the closed components mathematically
        visited_strands = set()
        closed_components = []
        R_OUT = 3.0  # Routing distance outside the braid core

        for start_s in range(num_strands):
            if start_s in visited_strands:
                continue

            current_s = start_s
            component_points = []

            while True:
                visited_strands.add(current_s)
                component_points.extend(strands[current_s])

                # The strand ended at X = current_pos[current_s].
                # We route it outside the braid back to Z = 0, at the exact same X.
                end_x = float(current_pos[current_s])

                # Return path trajectory
                component_points.append((end_x, 0.0, z_current + 1.0))
                component_points.append((end_x, R_OUT, z_current + 1.0))
                component_points.append((end_x, R_OUT, -1.0))
                component_points.append((end_x, 0.0, -1.0))
                component_points.append((end_x, 0.0, 0.0)) # Connects to start!

                # The start of the next strand is the one initially located at end_x
                next_s = end_x
                if next_s == start_s:
                    break # Loop closed!

                current_s = int(next_s)

            closed_components.append(component_points)

        return closed_components

# --- TEST THE NEW ENGINE ---
if __name__ == "__main__":
    try:
        import sstcore
    except ImportError:
        import sstbindings as sstcore

    # Dictionary of fundamental particles and their Braid Words
    test_braids = {
        "Unknot (Z-Boson/Higgs)": [1, -1],           # Trivial crossing that cancels out
        "Hopf Link (W-Boson)": [1, 1],               # n=2 link
        "Trefoil (Electron)": [1, 1, 1],             # 3_1 knot
        "Figure-Eight (Amphichiral)": [1, -2, 1, -2],# 4_1 knot
        "Torus 5_1 (Muon)": [1, 1, 1, 1, 1]          # 5_1 knot
    }

    print("\n=== SST BRAID GENERATOR TEST ===")

    for name, word in test_braids.items():
        print(f"\n[*] Generating {name} | Braid Word: {word}")

        # 1. Generate the raw 3D wireframe
        # We use num_strands=2 for standard 2-braids, except Figure-Eight which needs 3.
        strands_needed = max([abs(c) for c in word]) + 1 if word else 1
        raw_filaments = BraidTo3D.generate_filaments(word, num_strands=strands_needed)

        n_comp = len(raw_filaments)
        print(f"    [+] Topology traced: {n_comp} component(s)")

        # 2. Inject directly into C++
        particle = sstcore.ParticleEvaluator(raw_filaments)

        # Relax to physical Horn Torus
        try:
            particle.relax(iterations=1200, timestep=0.005)
            # Apply lambda stretch factor if it's a Boson (n>=2 or amphichiral)
            lambda_val = 3.16 if (n_comp >= 2 or name == "Figure-Eight (Amphichiral)") else 1.0

            L_tot = particle.get_dimless_ropelength(stretch_lambda=lambda_val)
            print(f"    [+] Stable Ab Initio L_tot: {L_tot:.3f} (Lambda stretch: {lambda_val})")
        except Exception as e:
            print(f"    [!] Relaxation failed: {e}")