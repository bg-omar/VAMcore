# fseries_compat.py
"""
Shared .fseries convention: file row index = harmonic index j.
All evaluators use j = 0 .. N-1 (explicit j=0 row, 6 columns per row).
Import parse_fseries_multi and eval_fourier_block from here everywhere Fourier is evaluated.
"""
import os
import numpy as np

try:
    from sstbindings import fourier_knot_eval
    HAVE_SST = True
except Exception:
    HAVE_SST = False


def _parse_floats_from_line(line: str):
    """Parse a whitespace-separated line into floats. Returns list[float] or None."""
    parts = line.strip().split()
    if not parts:
        return None
    try:
        return [float(x) for x in parts]
    except Exception:
        return None


def _normalize_leading_j0_row_if_needed(data_rows):
    """
    Normalize legacy .fseries where the first data row has only 3 columns (e.g. '0 0 0').
    If data_rows[0] has 3 floats and the next non-empty row has 6, set data_rows[0] = 6 zeros.
    """
    if not data_rows:
        return data_rows
    first = data_rows[0]
    if len(first) != 3:
        return data_rows
    nxt = None
    for k in range(1, len(data_rows)):
        if data_rows[k] is not None and len(data_rows[k]) > 0:
            nxt = data_rows[k]
            break
    if nxt is not None and len(nxt) == 6:
        data_rows[0] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    return data_rows


def _data_rows_to_coeffs(data_rows, path):
    """Normalize, validate 6 columns, and build coeffs dict from data_rows."""
    data_rows = _normalize_leading_j0_row_if_needed(data_rows)
    for idx, r in enumerate(data_rows):
        if len(r) != 6:
            raise ValueError(
                f"{os.path.basename(path)}: expected 6 columns per row in .fseries block, "
                f"but row {idx} has {len(r)} columns. Run canonicalizer to convert legacy format."
            )
    arr = np.asarray(data_rows, dtype=float)
    return {
        "a_x": arr[:, 0],
        "b_x": arr[:, 1],
        "a_y": arr[:, 2],
        "b_y": arr[:, 3],
        "a_z": arr[:, 4],
        "b_z": arr[:, 5],
    }


def parse_fseries_multi(filename):
    """
    Parse one .fseries file (multiple blocks allowed).
    Returns list of (header, coeffs) with coeffs = {a_x, b_x, a_y, b_y, a_z, b_z} (1D arrays).
    Convention: row index in file = harmonic index j (j=0..N-1).
    """
    knots = []
    header = None
    data_rows = []
    with open(filename) as f:
        for line in f:
            line_stripped = line.strip()
            if line_stripped.startswith('%'):
                if data_rows:
                    knots.append((header, _data_rows_to_coeffs(data_rows, filename)))
                    data_rows = []
                header = line_stripped.lstrip('%').strip()
                continue
            if not line_stripped and data_rows:
                knots.append((header, _data_rows_to_coeffs(data_rows, filename)))
                data_rows = []
                header = None
                continue
            row = _parse_floats_from_line(line)
            if row is not None:
                data_rows.append(row)
    if data_rows:
        knots.append((header, _data_rows_to_coeffs(data_rows, filename)))
    return knots


def eval_fourier_block(coeffs, s):
    """
    Evaluate x(s), y(s), z(s) from coeffs dict (a_x, b_x, a_y, b_y, a_z, b_z).
    Convention: j = 0 .. N-1 (row index = harmonic index).
    Uses sstbindings.fourier_knot_eval if available, else NumPy.
    Returns (x, y, z) as 1D arrays.
    """
    if HAVE_SST:
        x, y, z = fourier_knot_eval(
            coeffs['a_x'], coeffs['b_x'],
            coeffs['a_y'], coeffs['b_y'],
            coeffs['a_z'], coeffs['b_z'],
            s.astype(float)
        )
        return np.asarray(x), np.asarray(y), np.asarray(z)
    j = np.arange(coeffs['a_x'].size, dtype=float)[:, None]
    sj = j * s[None, :]
    cosj, sinj = np.cos(sj), np.sin(sj)
    def series(ax, bx):
        return (ax[:, None] * cosj + bx[:, None] * sinj).sum(axis=0)
    return (
        series(coeffs['a_x'], coeffs['b_x']),
        series(coeffs['a_y'], coeffs['b_y']),
        series(coeffs['a_z'], coeffs['b_z']),
    )
