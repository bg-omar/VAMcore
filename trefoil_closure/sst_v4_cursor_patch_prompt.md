# Cursor AI patch prompt — SST robustness sweep v4 + Qt monitor GUI

Patch the existing file `sst_ideal_trefoil_robustness_sweep_v3_project_run3.py` into a new file named:

`sst_ideal_trefoil_robustness_sweep_v4.py`

Also add a new GUI launcher file named:

`sst_trefoil_v4_gui.py`

Important constraints:
- Do **not** delete existing physics logic unless it is dead duplicated code proven unreachable.
- Prefer additive refactors and extraction into helper functions over behavior-changing rewrites.
- Preserve the current PyTorch acceleration path.
- Preserve the current local `ideal.txt` loading.
- Preserve the current optional local `sst_core.cpp` hot-build/import path.
- Preserve the current `a_nc` naming (do not reintroduce `a0`).
- Preserve current CSV/TXT/TeX outputs, but allow adding new outputs.
- Keep the script runnable from CLI exactly as before.

---

## Part A — Clean up run3 into a maintainable v4

The current run3 is functionally useful but has become structurally noisy. Produce `sst_ideal_trefoil_robustness_sweep_v4.py` with the following changes.

### 1. Backend architecture cleanup

Create a single explicit backend selector for the Biot–Savart scan.

Add:
- `BS_BACKEND_MODE = "auto"` with allowed values:
  - `"auto"`
  - `"local_cpp_scan"`
  - `"torch"`
  - `"numpy"`
- `detect_bs_backend()` returning a short string label.
- `scan_BS_energy_backend(...)` that routes to:
  - local C++ scan if available and selected,
  - otherwise torch if enabled,
  - otherwise numpy.

Rules:
- In `auto`, prefer local C++ scan, then torch, then numpy.
- Print the chosen backend once near startup and once per run block only if it changes.
- Record backend choice in each result row as `bs_backend`.

### 2. Deduplicate project-integration logic

Extract all project-integration code into a small cohesive section:
- `initialize_project_sources()`
- `load_ideal_coeffs_or_fallback()`
- `maybe_build_and_import_local_sst_core()`
- `summarize_project_sources()`

Acceptance:
- there should be only one place that decides whether `ideal.txt` is used,
- only one place that decides whether local `sst_core` is used,
- only one place that decides whether a local C++ scan backend is available.

### 3. Add timing instrumentation

Add high-level timings using `time.perf_counter()` for:
- total script runtime,
- per `(N_geom, N_int_target)` geometry build,
- per `(N_geom, N_int_target)` BS scan,
- per fit extraction block,
- per full run row group.

Store in each CSV row:
- `t_geometry_s`
- `t_scan_s`
- `t_fit_s`
- `t_total_block_s`

Also print concise timing lines to stdout.

### 4. Add reproducibility metadata

Add to startup output and to a JSON sidecar file:
- python version,
- platform,
- torch version if present,
- chosen torch device if present,
- whether local `sst_core` loaded,
- whether local C++ cutoff scan loaded,
- source path of `ideal.txt`,
- knot id,
- mode (`ideal` or `torus`),
- backend mode.

Write to:
- `run_metadata_v4.json`

### 5. Best-estimate cleanup

Keep the current best-estimate outputs, but extend them to report two views:

1. `best_estimate_practical`
- best preferred-fit no-contact run chosen by current heuristics.

2. `best_estimate_asymptotic`
- use the two highest available `N_int_actual` values at the preferred fit method and `lambda_K = 0`,
- compute midpoint and half-range for:
  - `A_K`
  - `A_ratio`
  - `a_nc_over_rc`

Write all of this into:
- `final_best_estimate_v4.csv`
- `final_best_estimate_v4.txt`
- `final_best_estimate_v4.tex`

### 6. Optional fast-run mode

Add CLI preset:
- `--preset fast`
- `--preset full`

Behavior:
- `fast` uses smaller default sweep lists for quick UI testing.
- `full` preserves current broader sweep.
- CLI overrides still win over presets.

### 7. Safer CLI options

Add optional CLI args:
- `--output-dir`
- `--backend`
- `--knot-id`
- `--max-fourier-mode`
- `--n-geom-list 4000,8000,...`
- `--n-int-list 2000,4000,...`
- `--lambda-list 0,1e-3,...`
- `--plateau-fracs 0.08,0.12,0.16`
- `--no-torch`
- `--no-local-sst-core`
- `--no-auto-compile`

Do not break current zero-argument execution.

### 8. Keep log lines parse-friendly

Standardize important stdout lines so they are easy for the GUI to parse.

Use stable prefixes exactly like:
- `[META] ...`
- `[BACKEND] ...`
- `[GEOM] ...`
- `[SCAN] ...`
- `[FIT] ...`
- `[ROOT] ...`
- `[BEST] ...`
- `[TIME] ...`
- `[WARN] ...`
- `[ERROR] ...`

Examples:
- `[FIT] N_geom=16000 N_int=16000 method=plateau_0.12 A_K=0.07934203 A_ratio=0.997041 a_nc_over_rc=0.998520`
- `[BACKEND] bs_backend=local_cpp_scan`

### 9. Leave physics formulas unchanged unless only names change

Do not alter these formulas except for variable naming consistency:
- Fourier curve evaluation
- Biot–Savart scan definition
- local slope extraction for `A_K`
- no-contact radius `a_nc`
- regularized energy and root search

The goal is code quality, speed routing, logging clarity, and GUI integration — not a new physics model.

---

## Part B — Add the Qt GUI monitor

Create a new file:

`sst_trefoil_v4_gui.py`

Use `PyQt5` because the project already has a `PyQt5` + `QWebEngineView` GUI pattern.

### 1. GUI layout

Create a desktop app with four visible regions:

1. **Top control bar**
- script selector (default `sst_ideal_trefoil_robustness_sweep_v4.py`)
- preset selector (`fast`, `full`)
- backend selector (`auto`, `local_cpp_scan`, `torch`, `numpy`)
- mode selector (`ideal`, `torus`)
- output dir field
- Run button
- Stop button
- Open output folder button

2. **Left status panel**
Cards showing parsed live values:
- backend
- knot id
- ideal source
- local sst_core yes/no
- A_req
- latest `A_K`
- latest `A_ratio`
- latest `a_nc/r_c`
- latest `a*/r_c`
- latest `N_geom`
- latest `N_int`
- total elapsed time

3. **Center terminal panel**
A dark `QPlainTextEdit` that shows raw stdout/stderr exactly as emitted.
This is the “Qt terminal”.

4. **Right rich info panel**
A `QWebEngineView` with:
- KaTeX-rendered formulas used by the script,
- a scrolling rich log view where parsed events are shown as cards,
- extra explanatory text for recognized log events.

### 2. Formula panel content

Render these formulas with KaTeX:
- `X(t) = \sum_k [A_k \cos(2\pi k t) + B_k \sin(2\pi k t)]`
- `E_{BS}(a)` scan concept
- `A_K` from local slope of `E_{BS}/L_K` versus `-\ln a`
- `a_{\mathrm{nc}} = \sqrt{A_K/\pi}\,\Gamma_0/\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}`
- `E_K(a)` with BS + core + contact terms
- `a^* = \arg\min E_K(a)`
- `A_{\mathrm{req}} = 1/(4\pi)`

### 3. Parse stdout into structured cards

Implement a worker thread that runs the target script as a subprocess with unbuffered output.
Capture stdout and stderr line by line.

Parse the standardized prefixes from Part A.
For recognized lines, append a card to the rich panel with:
- short title,
- raw values,
- one-sentence interpretation.

Examples:
- for `[FIT] ...` show whether `A_K` is above/below/near `1/(4π)`
- for `[BACKEND] ...` explain which acceleration path is active
- for `[TIME] ...` show elapsed phase timing
- for `[BEST] ...` show current best-estimate summary

### 4. Output artifact panel

Add a small list or buttons for known output files if they appear:
- CSV summary
- best-estimate CSV/TXT/TeX
- summary PNGs

Allow opening them from the GUI via desktop services.

### 5. Stability and usability

Requirements:
- GUI must not freeze while the script runs.
- Stop button must terminate the subprocess safely.
- Use dark theme matching the current aesthetic in `main_gui.py`.
- Escape HTML safely when injecting raw text into the web view.
- Preserve KaTeX rendering after dynamically appending cards.

### 6. Reuse from existing GUI

The current `main_gui.py` already demonstrates:
- local `sst_core.cpp` hot-build logic,
- `QWebEngineView` rich output,
- KaTeX auto-render pattern. Use that style as the baseline. fileciteturn9file0

Do not delete that file. Add the new GUI as a separate file.

---

## Part C — Acceptance checks

When done, the following should hold:

1. `python sst_ideal_trefoil_robustness_sweep_v4.py` runs from CLI.
2. `python sst_trefoil_v4_gui.py` opens a GUI.
3. Running from the GUI shows raw terminal output live.
4. The right panel shows formulas rendered with KaTeX.
5. Parsed `[FIT]` lines update the status cards.
6. The GUI can stop a run.
7. The GUI can open the output directory.
8. Existing PyTorch acceleration still works.
9. If local `sst_core` scan is available, it is used in `auto` mode.
10. Output files include v4 best-estimate files plus metadata JSON.

---

## Part D — Keep the implementation practical

Do not over-engineer. Prefer:
- one subprocess worker class,
- one parser helper,
- one main window class,
- one HTML template string with KaTeX,
- one small status-card update function.

Deliver production-usable code, not pseudocode.
