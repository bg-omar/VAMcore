import requests
import gzip
import shutil
import numpy as np
import re
import os
from pathlib import Path
from sst_exports import get_exports_dir

def prepare_database(url="https://katlas.org/images/d/d2/Ideal.txt.gz", gz_name="Ideal.txt.gz", txt_name="Ideal.txt"):
    """Autonome acquisitie en extractie van de topologische referentiedatabase."""
    gz_path = Path(gz_name)
    txt_path = Path(txt_name)

    if not txt_path.exists():
        if not gz_path.exists():
            print(f"[*] Acquireren van referentiedatabase via {url}...")
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            gz_path.write_bytes(r.content)

        print(f"[*] Decomprimeren van database archief...")
        with gzip.open(gz_path, "rb") as f_in, open(txt_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    return str(txt_path)

def extract_ab_block(text: str, ab_id: str) -> str:
    m = re.search(rf'<AB\s+Id="{re.escape(ab_id)}"[^>]*>', text)
    if not m:
        raise ValueError(f"AB Id '{ab_id}' niet gevonden in de database.")
    end = text.find("</AB>", m.end())
    return text[m.start(): end + len("</AB>")]

def parse_coeffs(ab_block: str):
    coeffs = {}
    for m in re.finditer(r'<Coeff\s+I="\s*([0-9]+)"\s+A="\s*([^"]+)"\s+B="\s*([^"]+)"\s*/>', ab_block):
        i = int(m.group(1))
        A = list(map(float, m.group(2).replace(" ", "").split(",")))
        B = list(map(float, m.group(3).replace(" ", "").split(",")))
        coeffs[i] = (A, B)
    return coeffs

def generate_sst_pipeline(ab_id, knot_name, max_j_out=50, iterations=1500, num_points=300, out_dir=None):
    """out_dir: map voor .fseries; default = get_exports_dir()."""
    if out_dir is None:
        out_dir = get_exports_dir()
    else:
        out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n[*] Start SST-integratie pipeline: {knot_name} (AB Id: {ab_id})")

    db_path = prepare_database()
    ideal_data = Path(db_path).read_text(encoding="utf-8", errors="ignore")

    try:
        block = extract_ab_block(ideal_data, ab_id)
        raw_coeffs = parse_coeffs(block)
    except Exception as e:
        print(f"[!] Extractiefout: {e}")
        return

    # Ruimtelijke reconstructie
    max_j_in = max(raw_coeffs.keys())
    t = np.linspace(0, 2*np.pi, num_points, endpoint=False)
    pts = np.zeros((num_points, 3))

    for j in range(1, max_j_in + 1):
        if j in raw_coeffs:
            A, B = raw_coeffs[j]
            ax, ay, az = A; bx, by, bz = B
            cos_jt = np.cos(j * t)
            sin_jt = np.sin(j * t)
            pts[:, 0] += ax * cos_jt + bx * sin_jt
            pts[:, 1] += ay * cos_jt + by * sin_jt
            pts[:, 2] += az * cos_jt + bz * sin_jt

    def normalize_arclength(points, N):
        dp = np.diff(np.vstack((points, [points[0]])), axis=0)
        ds = np.linalg.norm(dp, axis=1)
        s = np.zeros(len(points)+1)
        s[1:] = np.cumsum(ds)
        L = s[-1]
        s_target = np.linspace(0, L, N, endpoint=False)
        pts_uniform = np.zeros((N, 3))
        for dim in range(3):
            pts_uniform[:, dim] = np.interp(s_target, s, np.append(points[:, dim], points[0, dim]))
        return pts_uniform

    pts = normalize_arclength(pts, num_points)

    # Hamiltoniaanse Gradient Afstroming
    print(f"[*] Minimaliseren van interactie-energie ({iterations} iteraties)...")
    k_spring = 5.0
    q_repulse = 0.05
    alpha = 0.005

    for step in range(iterations):
        lengths = np.linalg.norm(np.diff(np.vstack((pts, [pts[0]])), axis=0), axis=1)
        l0 = np.mean(lengths)

        pts_next = np.roll(pts, -1, axis=0)
        pts_prev = np.roll(pts, 1, axis=0)

        v_next = pts_next - pts
        d_next = np.linalg.norm(v_next, axis=1, keepdims=True)
        f_next = k_spring * (d_next - l0) * (v_next / (d_next + 1e-9))

        v_prev = pts_prev - pts
        d_prev = np.linalg.norm(v_prev, axis=1, keepdims=True)
        f_prev = k_spring * (d_prev - l0) * (v_prev / (d_prev + 1e-9))

        f_elastic = f_next + f_prev

        diff = pts[:, np.newaxis, :] - pts[np.newaxis, :, :]
        dist = np.linalg.norm(diff, axis=2)

        mask = np.ones((num_points, num_points), dtype=bool)
        np.fill_diagonal(mask, False)
        for i in range(num_points):
            mask[i, (i+1)%num_points] = False
            mask[i, (i-1)%num_points] = False

        dist[~mask] = 1e9
        f_rep_mag = q_repulse / (dist**3 + 1e-9)
        f_rep_mag[~mask] = 0.0

        f_repulsion = np.sum(diff * f_rep_mag[:, :, np.newaxis], axis=1)

        grad = -f_elastic - f_repulsion
        grad_norm = np.linalg.norm(grad, axis=1, keepdims=True)
        grad = np.where(grad_norm > 5.0, grad * (5.0 / grad_norm), grad)

        pts -= alpha * grad
        pts -= np.mean(pts, axis=0)

    pts = normalize_arclength(pts, num_points)

    # Spectrale Fourier Projectie
    print(f"[*] Transformeren naar SST Canon format (j_max = {max_j_out})...")
    s_param = np.linspace(0, 2*np.pi, num_points, endpoint=False)

    def calculate_fourier(coord, s, maxJ):
        a, b = np.zeros(maxJ), np.zeros(maxJ)
        for j in range(1, maxJ + 1):
            a[j-1] = (2 / num_points) * np.sum(coord * np.cos(j * s))
            b[j-1] = (2 / num_points) * np.sum(coord * np.sin(j * s))
        return a, b

    ax, bx = calculate_fourier(pts[:, 0], s_param, max_j_out)
    ay, by = calculate_fourier(pts[:, 1], s_param, max_j_out)
    az, bz = calculate_fourier(pts[:, 2], s_param, max_j_out)

    out_path = out_dir / f"{knot_name}_sst.fseries"
    with open(out_path, 'w') as f:
        f.write(f"% (Fourier projection from Ideal database for SST Canon: {knot_name} | AB Id: {ab_id})\n")
        f.write("% row index = j (row0 j=0, row1 j=1, ...). a_x(j) b_x(j) a_y(j) b_y(j) a_z(j) b_z(j)\n")
        # j=0 row (6 zeros) before harmonics so .fseries has explicit j=0..J convention
        f.write(" 0.000000  0.000000  0.000000  0.000000  0.000000  0.000000\n")
        for j in range(max_j_out):
            f.write(f"{ax[j]: 9.6f} {bx[j]: 9.6f} {ay[j]: 9.6f} {by[j]: 9.6f} {az[j]: 9.6f} {bz[j]: 9.6f}\n")


    print(f"[+] Succes! Geoptimaliseerde inbedding weggeschreven naar '{out_path}'")



# Mapping van standaardnomenclatuur naar KnotServer AB Id's (gebruikt door batch en GUI)
knopen_catalogus = {
    "3_1": "3:1:1",   # Trefoil knot (Torus)
    "4_1": "4:1:1",   # Figure-eight knot (Twist)
    "5_1": "5:1:1",   # Torus knot
    "5_2": "5:1:2",   # Three-twist knot
    "6_1": "6:1:1",   # Stevedore knot (Twist)
    "7_1": "7:1:1",   # Torus knot
    "7_2": "7:1:2",   # Five-twist knot
    "8_1": "8:1:1",   # Six-twist knot
    "9_1": "9:1:1",   # Torus knot
    "9_2": "9:1:2",   # Twist-gerelateerd
    "10_1": "10:1:1"  # Twist-gerelateerd
}


def run_batch_from_catalog(max_j_out=50, iterations=1500, num_points=300, out_dir=None):
    """Genereer .fseries voor alle knopen in knopen_catalogus. out_dir default = get_exports_dir()."""
    for naam, ab_id in knopen_catalogus.items():
        try:
            generate_sst_pipeline(ab_id=ab_id, knot_name=f"knot_{naam}",
                                  max_j_out=max_j_out, iterations=iterations, num_points=num_points,
                                  out_dir=out_dir)
        except Exception as e:
            print(f"[!] Fout bij het verwerken van {naam} ({ab_id}): {e}")


if __name__ == "__main__":
    import sys
    if "--batch" not in sys.argv:
        print("Usage: python generate_knot_fseries.py --batch   # genereer alle knopen uit catalogus")
        print("Of open de GUI (GUI_SST_Knot_fseries) en gebruik 'Generate all knots from catalog'.")
        sys.exit(0)
    print(f"\n[*] Start batch-verwerking van {len(knopen_catalogus)} SST topologieën...\n")
    run_batch_from_catalog()
    print("\n[+] Batch-executie voltooid. Alle monocomponente .fseries bestanden zijn gegenereerd.")