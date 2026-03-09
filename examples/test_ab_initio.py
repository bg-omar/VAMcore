import sstcore as sstbindings
import time

# De Catalogus beheert de vaste topologische invarianten
KNOT_INVARIANTS = {
    "3:1:1":  {"name": "Electron",  "k": 3.0,   "g": 1, "chi": 2.0},
    "5:1:2":  {"name": "Up Quark",  "k": 1.388, "g": 1, "chi": 2.0},
    "10:1:1": {"name": "Top Quark", "k": 2.561, "g": 1, "chi": 2.0}
}

def evaluate_particle(knot_id):
    props = KNOT_INVARIANTS.get(knot_id)
    if not props:
        return

    print(f"\n[*] Evalueren van {props['name']} ({knot_id})...")
    start = time.time()

    # MAGIE: C++ leest hier zélf Ideal.txt uit zijn eigen ingebakken geheugen!
    particle = sstbindings.ParticleEvaluator(knot_id, resolution=4000)

    # C++ Relaxatie
    particle.relax(iterations=2500, timestep=0.005)

    # C++ berekent de kwantummassa
    mass_kg = particle.compute_mass_kg(chi_spin=props['chi'], k=props['k'], g=props['g'])
    mass_mev = mass_kg / 1.78266192e-30

    print(f"[+] Evaluatie voltooid in {time.time() - start:.3f} sec.")
    print(f"    SST Invariante Massa : {mass_kg:.4e} kg")
    print(f"    PDG Equivalente Massa: {mass_mev:.3f} MeV/c^2")

if __name__ == "__main__":
    evaluate_particle("3:1:1")
    evaluate_particle("5:1:2")
    evaluate_particle("10:1:1")