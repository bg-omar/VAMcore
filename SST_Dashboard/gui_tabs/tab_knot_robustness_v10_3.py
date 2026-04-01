# gui_tabs/tab_knot_robustness_v10_3.py — v10.3 sweep: subprocess + KaTeX monitor (plan: Option A)
from __future__ import annotations

import html
import json
import os
import re
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtWidgets import (
    QCheckBox, QComboBox, QFileDialog, QFormLayout, QFrame,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPlainTextEdit,
    QPushButton, QScrollArea, QSpinBox, QSplitter, QTabWidget, QVBoxLayout, QWidget,
)

_DASH = Path(__file__).resolve().parent.parent
_SST = _DASH.parent
TREFOIL = _DASH / "trefoil_closure"
SCRIPT = TREFOIL / "sst_knot_candidate_robustness_sweep_v10_3_master_sweep.py"


def _get_build_robustness_arg_parser():
    """Import sweep module's parser for argv validation (single source of truth)."""
    tc = str(TREFOIL)
    if tc not in sys.path:
        sys.path.insert(0, tc)
    import sst_knot_candidate_robustness_sweep_v10_3_master_sweep as _mod

    return _mod.build_robustness_arg_parser


try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    _WEB = True
except Exception:
    QWebEngineView = None
    _WEB = False

FIT_RE = re.compile(
    r"\[FIT\]\s+N_geom=(?P<N_geom>\d+)\s+N_int=(?P<N_int>\d+)\s+method=(?P<method>[^\s]+)\s+"
    r"A_K=(?P<A_K>[-+0-9.eE]+)\s+A_ratio=(?P<A_ratio>[-+0-9.eE]+)\s+a_nc_over_rc=(?P<a_nc>[-+0-9.eE]+)"
)
BACKEND_RE = re.compile(r"\[BACKEND\]\s+bs_backend=(?P<backend>[^\s]+)")
META_RE = re.compile(r"\[META\]\s+(?P<key>[A-Za-z0-9_./ -]+?)\s*[:=]\s*(?P<value>.+)")
ROOT_RE = re.compile(r"\[ROOT\].*a_star_over_rc=(?P<a_star>[-+0-9.eE]+)")
TIME_RE = re.compile(r"\[TIME\]\s+(?P<label>[^:=]+?)(?:_s)?[:=]\s*(?P<value>[-+0-9.eE]+)")
BEST_RE = re.compile(r"\[BEST\]\s+(?P<body>.+)")
THEOREM_RE = re.compile(r"\[THEOREM\]\s+(?P<body>.+)")
CHECK_RE = re.compile(
    r"\[CHECK\].*method=(?P<method>[^\s]+).*closure_x=(?P<closure_x>[-+0-9.eE]+).*closure_x_minus_1=(?P<delta>[-+0-9.eE]+)"
)
CONT_RE = re.compile(
    r"\[CONT\].*lambda_K=(?P<lam>[-+0-9.eE]+).*prev_a_star_over_rc=(?P<prev>[^\s]+).*a_star_over_rc=(?P<curr>[-+0-9.eE]+).*jump=(?P<jump>[^\s]+).*root_choice=(?P<choice>[^\s]+)"
)
BARRIER_RE = re.compile(
    r"\[BARRIER\].*lambda_K=(?P<lam>[-+0-9.eE]+).*beta=(?P<beta>[-+0-9.eE]+).*contact_force_at_x1=(?P<cf>[-+0-9.eE]+).*F_at_x1=(?P<Fx1>[-+0-9.eE]+).*contact_model=(?P<model>[^\s]+)"
)


def he(s: str) -> str:
    return html.escape(s, quote=True)


FORMULAS_MONITOR = [
    ("Biot–Savart scan", r"E_{BS}(a)\;\text{sampled over cutoff}\; a"),
    ("Slope extraction", r"A_K\approx \frac{d(E_{BS}/L_K)}{d(-\ln a)}"),
    ("No-contact radius", r"a_{\mathrm{nc}}=\sqrt{A_K/\pi}\,\Gamma_0/\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}"),
    ("Closure benchmark", r"A_{\mathrm{req}}=\frac{1}{4\pi}"),
]

FORMULAS_THEOREM = [
    ("No-contact target", r"\frac{a_{\mathrm{nc}}}{r_c}=\sqrt{4\pi A_K}"),
    ("Dimensionless stationarity", r"F(x)=0,\quad x=a/r_c"),
    ("Barrier-flat condition", r"\left.\frac{dE_{\mathrm{cont}}}{da}\right|_{a=r_c}=0"),
    ("Closure residual", r"\Delta_{\mathrm{closure}}=\sqrt{4\pi A_K}-1"),
]


def _formula_cards_html(formulas: List[Tuple[str, str]]) -> str:
    return "".join(
        f"<div class='formula-card'><div class='formula-title'>{he(title)}</div>"
        f"<div class='formula-body'>$$ {latex} $$</div></div>"
        for title, latex in formulas
    )


def build_html_shell(formulas: List[Tuple[str, str]], initial_title: str, initial_meta: str) -> str:
    """KaTeX shell aligned with sst_trefoil_v5_gui_extra_tab.build_html_shell."""
    formula_html = _formula_cards_html(formulas)
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
  <style>
    body {{ background:#16181d; color:#d6d9df; font-family:Segoe UI,Arial,sans-serif; margin:0; padding:0; }}
    #wrap {{ display:flex; flex-direction:column; gap:14px; padding:14px; }}
    .section-title {{ color:#8fb7ff; font-weight:700; font-size:15px; margin:0 0 8px 0; }}
    #formula-grid {{ display:grid; grid-template-columns:1fr; gap:8px; }}
    .formula-card, .event-card {{ background:#20242c; border:1px solid #2d3340; border-radius:10px; padding:10px 12px; box-shadow:0 2px 8px rgba(0,0,0,.25); }}
    .formula-title, .event-title {{ font-weight:700; color:#eef3ff; margin-bottom:6px; }}
    .formula-body {{ color:#cfd6e6; overflow-x:auto; }}
    #events {{ display:flex; flex-direction:column; gap:8px; }}
    .event-meta {{ color:#aab4c6; font-size:12px; margin-top:4px; }}
    .event-raw {{ color:#9fb0c4; white-space:pre-wrap; word-break:break-word; font-family:Consolas,monospace; font-size:12px; margin-top:6px; }}
    .ok {{ border-left:4px solid #3fb950; }}
    .warn {{ border-left:4px solid #d29922; }}
    .info {{ border-left:4px solid #58a6ff; }}
    .err {{ border-left:4px solid #f85149; }}
  </style>
</head>
<body>
<div id="wrap">
  <div>
    <div class="section-title">SST formulas</div>
    <div id="formula-grid">{formula_html}</div>
  </div>
  <div>
    <div class="section-title">Structured events</div>
    <div id="events">
      <div class="event-card info"><div class="event-title">{he(initial_title)}</div><div class="event-meta">{he(initial_meta)}</div></div>
    </div>
  </div>
</div>
<script>
function renderMath(scope) {{
  if (typeof renderMathInElement === 'function') {{
    renderMathInElement(scope || document.body, {{
      delimiters:[
        {{left:'$$', right:'$$', display:true}},
        {{left:'$', right:'$', display:false}}
      ]
    }});
  }}
}}
window.addEventListener('load', () => renderMath(document.body));
function appendEvent(kind, title, body, raw, meta) {{
  const card = document.createElement('div');
  card.className = 'event-card ' + (kind || 'info');
  card.innerHTML = `<div class="event-title">${{title}}</div><div>${{body}}</div><div class="event-meta">${{meta||''}}</div><div class="event-raw">${{raw||''}}</div>`;
  document.getElementById('events').prepend(card);
  renderMath(card);
}}
</script>
</body>
</html>"""


class ProcessWorker(QThread):
    line_signal = pyqtSignal(str)
    mon_signal = pyqtSignal(dict)
    th_signal = pyqtSignal(dict)
    state_signal = pyqtSignal(str)

    def __init__(self, cmd: List[str], cwd: Path):
        super().__init__()
        self.cmd, self.cwd, self.proc = cmd, cwd, None
        self._stop = False

    def stop(self):
        self._stop = True
        if self.proc:
            try:
                self.proc.terminate() if os.name == "nt" else self.proc.send_signal(signal.SIGTERM)
            except Exception:
                pass

    def _mon(self, d: dict):
        self.mon_signal.emit(d)

    def _th(self, d: dict):
        self.th_signal.emit(d)

    def _parse(self, line: str):
        line = line.rstrip("\n")
        m = FIT_RE.search(line)
        if m:
            ar = float(m.group("A_ratio"))
            body = (
                f"Method <b>{he(m.group('method'))}</b> at $N_{{\\mathrm{{geom}}}}={m.group('N_geom')}$, "
                f"$N_{{\\mathrm{{int}}}}={m.group('N_int')}$ gives "
                f"$A_K={float(m.group('A_K')):.8f}$, "
                f"$A_K/A_{{\\mathrm{{req}}}}={ar:.6f}$, "
                f"$a_{{\\mathrm{{nc}}}}/r_c={float(m.group('a_nc')):.6f}$."
            )
            k = "ok" if abs(ar - 1.0) < 0.01 else ("info" if abs(ar - 1.0) < 0.05 else "warn")
            self._mon(
                {
                    "kind": k,
                    "title": "Fit update",
                    "body": body,
                    "raw": line,
                    "meta": f"method={m.group('method')}",
                    "values": {
                        "latest_A_K": f"{float(m.group('A_K')):.8f}",
                        "latest_A_ratio": f"{ar:.6f}",
                        "latest_a_nc_over_rc": f"{float(m.group('a_nc')):.6f}",
                        "latest_N_geom": m.group("N_geom"),
                        "latest_N_int": m.group("N_int"),
                    },
                }
            )
            return
        m = BACKEND_RE.search(line)
        if m:
            backend = m.group("backend")
            explain = {
                "local_cpp_scan": "Local C++ cutoff scan is active.",
                "torch": "PyTorch acceleration is active.",
                "numpy": "Pure NumPy path is active; slow but reference-safe.",
            }.get(backend, "Backend selected.")
            self._mon(
                {
                    "kind": "info",
                    "title": "Backend",
                    "body": he(explain),
                    "raw": line,
                    "meta": backend,
                    "values": {"backend": backend},
                }
            )
            return
        m = META_RE.search(line)
        if m:
            key = m.group("key").strip()
            value = m.group("value").strip()
            vals: Dict[str, str] = {}
            lower = key.lower()
            if "knot" in lower:
                vals["knot_id"] = value
            elif "ideal source" in lower or "ideal_source" in lower:
                vals["ideal_source"] = value
            elif "local sst_core" in lower:
                vals["local_sst_core"] = value
            elif key.strip() == "A_req":
                vals["A_req"] = value
            self._mon(
                {
                    "kind": "info",
                    "title": key,
                    "body": he(value),
                    "raw": line,
                    "meta": "metadata",
                    "values": vals,
                }
            )
            return
        m = ROOT_RE.search(line)
        if m:
            self._mon(
                {
                    "kind": "info",
                    "title": "Regularized minimum",
                    "body": f"Latest selected branch gives $a^*/r_c={float(m.group('a_star')):.6f}$.",
                    "raw": line,
                    "meta": "root",
                    "values": {"latest_a_star_over_rc": f"{float(m.group('a_star')):.6f}"},
                }
            )
            return
        m = TIME_RE.search(line)
        if m:
            self._mon(
                {
                    "kind": "info",
                    "title": f"Timing — {he(m.group('label'))}",
                    "body": f"Elapsed time: <b>{float(m.group('value')):.3f} s</b>.",
                    "raw": line,
                    "meta": "timing",
                    "values": {"elapsed_hint": f"{float(m.group('value')):.3f} s"},
                }
            )
            return
        m = BEST_RE.search(line)
        if m:
            self._mon(
                {
                    "kind": "ok",
                    "title": "Best-estimate update",
                    "body": he(m.group("body")),
                    "raw": line,
                    "meta": "best",
                    "values": {},
                }
            )
            return
        m = THEOREM_RE.search(line)
        if m:
            self._th(
                {
                    "kind": "info",
                    "title": "Theorem target",
                    "body": he(m.group("body")),
                    "raw": line,
                    "meta": "theorem",
                    "values": {},
                }
            )
            return
        m = CHECK_RE.search(line)
        if m:
            d = float(m.group("delta"))
            k = "ok" if abs(d) < 1e-2 else ("info" if abs(d) < 5e-2 else "warn")
            self._th(
                {
                    "kind": k,
                    "title": f"No-contact closure check — {he(m.group('method'))}",
                    "body": (
                        f"$x_{{\\mathrm{{closure}}}}=\\sqrt{{4\\pi A_K}}={float(m.group('closure_x')):.8f}$, "
                        f"so $x_{{\\mathrm{{closure}}}}-1={d:.3e}$."
                    ),
                    "raw": line,
                    "meta": "closure_x",
                    "values": {
                        "closure_x": f"{float(m.group('closure_x')):.8f}",
                        "closure_x_minus_1": f"{d:.3e}",
                    },
                }
            )
            return
        m = CONT_RE.search(line)
        if m:
            jump_text = m.group("jump")
            try:
                jump = float(jump_text)
                k = "ok" if abs(jump) < 5e-3 else ("info" if abs(jump) < 2e-2 else "warn")
            except Exception:
                jump = None
                k = "info"
            body = (
                f"At $\\lambda_K={float(m.group('lam')):.4g}$ the selected branch is "
                f"$a^*/r_c={float(m.group('curr')):.6f}$ using <b>{he(m.group('choice'))}</b>."
            )
            if jump is not None:
                body += f" Branch jump diagnostic: $\\Delta={jump:.3e}$."
            self._th(
                {
                    "kind": k,
                    "title": "Continuation step",
                    "body": body,
                    "raw": line,
                    "meta": f"lambda={m.group('lam')}",
                    "values": {
                        "continuation_jump": jump_text,
                        "latest_a_star_over_rc": f"{float(m.group('curr')):.6f}",
                    },
                }
            )
            return
        m = BARRIER_RE.search(line)
        if m:
            cf = float(m.group("cf"))
            fx1 = float(m.group("Fx1"))
            k = "ok" if abs(cf) < 1e-8 and abs(fx1) < 1e-2 else ("info" if abs(fx1) < 5e-2 else "warn")
            self._th(
                {
                    "kind": k,
                    "title": "Barrier / full-model check",
                    "body": (
                        f"Contact model <b>{he(m.group('model'))}</b> at $\\lambda_K={float(m.group('lam')):.4g}$ gives "
                        f"$\\beta={float(m.group('beta')):.6f}$, "
                        f"$C(1)={cf:.3e}$, "
                        f"$F(1)={fx1:.3e}$."
                    ),
                    "raw": line,
                    "meta": "barrier",
                    "values": {
                        "contact_force_at_x1": f"{cf:.3e}",
                        "F_at_x1": f"{fx1:.3e}",
                        "contact_model": m.group("model"),
                    },
                }
            )
            return
        if line.startswith("[WARN]"):
            self._mon({"kind": "warn", "title": "Warning", "body": he(line[6:].strip()), "raw": line, "meta": "warning", "values": {}})
            return
        if line.startswith("[ERROR]"):
            self._mon({"kind": "err", "title": "Error", "body": he(line[7:].strip()), "raw": line, "meta": "error", "values": {}})
            self._th({"kind": "err", "title": "Error", "body": he(line[7:].strip()), "raw": line, "meta": "error", "values": {}})
            return

    def run(self):
        self.state_signal.emit("starting")
        env = os.environ.copy()
        env.setdefault("PYTHONUNBUFFERED", "1")
        cf = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        self.proc = subprocess.Popen(self.cmd, cwd=str(self.cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, bufsize=1, env=env, creationflags=cf)
        self.state_signal.emit("running")
        assert self.proc.stdout
        for line in self.proc.stdout:
            self.line_signal.emit(line)
            self._parse(line)
            if self._stop:
                break
        rc = self.proc.wait()
        self.state_signal.emit(f"finished:{rc}")


class StatusCard(QFrame):
    def __init__(self, title: str):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("QFrame{background:#20242c;border:1px solid #2d3340;border-radius:8px;} QLabel{color:#d8deeb;}")
        lay = QVBoxLayout(self)
        t = QLabel(title)
        t.setStyleSheet("font-weight:700;color:#8fb7ff;")
        self.v = QLabel("—")
        self.v.setWordWrap(True)
        self.v.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lay.addWidget(t)
        lay.addWidget(self.v)

    def setv(self, x: str):
        self.v.setText(x or "—")


class TabKnotRobustnessV103(QWidget):
    def __init__(self, p=None):
        super().__init__(p)
        self.worker = None
        self.w: Dict[str, Any] = {}
        self.cards: Dict[str, StatusCard] = {}
        L = QVBoxLayout(self)
        if not SCRIPT.is_file():
            L.addWidget(QLabel(f"Script missing:\n{SCRIPT}"))
            return
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        iw = QWidget()
        il = QVBoxLayout(iw)

        def add_form(title: str, rows: List[Tuple[Any, ...]]) -> None:
            g = QGroupBox(title)
            f = QFormLayout(g)
            for row in rows:
                if len(row) == 4:
                    label, kind, key, tip = row
                else:
                    label, kind, key = row
                    tip = ""
                wgt: QWidget
                if kind == "combo":
                    cb = QComboBox()
                    cb.addItems(key)
                    self.w[label] = cb
                    wgt = cb
                    f.addRow(label + ":", cb)
                elif kind == "line":
                    le = QLineEdit()
                    if isinstance(key, str):
                        if key.startswith("optional"):
                            le.setPlaceholderText(key)
                        elif key == "":
                            pass
                        else:
                            le.setText(key)
                            le.setPlaceholderText(key)
                    self.w[label] = le
                    wgt = le
                    f.addRow(label + ":", le)
                elif kind == "spin":
                    sp = QSpinBox()
                    sp.setRange(key[0], key[1])
                    sp.setValue(key[2])
                    self.w[label] = sp
                    wgt = sp
                    f.addRow(label + ":", sp)
                elif kind == "chk":
                    c = QCheckBox(label)
                    c.setChecked(bool(key))
                    self.w[label] = c
                    wgt = c
                    f.addRow(c)
                else:
                    continue
                if tip:
                    wgt.setToolTip(tip)
            il.addWidget(g)

        add_form("Run / parallel", [
            ("Mode", "combo", ["ideal", "torus"], "Sweep geometry mode."),
            ("Preset", "combo", ["fast", "full"], "fast = smaller grid for UI tests; full = default sweep."),
            ("Backend", "combo", ["auto", "local_cpp_scan", "torch", "numpy"], "Biot–Savart backend."),
            ("Sweep layout", "combo", ["matrix", "exact_pairs_only", "theorem_ladder"], "How N_geom:N_int grid is built."),
            ("Parallel scope", "combo", ["auto", "none", "geom", "global"], "ProcessPool scope."),
            ("Max workers (0=auto)", "spin", (0, 256, 0), "0 lets the script pick worker count."),
        ])
        add_form("Knots", [
            ("Knot id", "line", "3:1:1", "Single knot when list and preset are empty."),
            ("Knot list", "line", "optional batch", "Comma/space-separated ids; @group names allowed."),
            ("Knot preset", "line", "leptons / quarks / …", "Built-in group name(s)."),
            ("External knotlib", "combo", ["auto", "none", "spherogram"], "Optional spherogram helper."),
        ])
        add_form("Grids (empty = defaults)", [
            ("N geom list", "line", "", "Comma-separated, e.g. 4000,8000,16000"),
            ("N int list", "line", "", "Comma-separated integration counts."),
            ("Lambda list", "line", "", "Comma-separated λ values."),
            ("Plateau fracs", "line", "", "Comma-separated plateau fractions."),
            ("Extra target pairs", "line", "", "Exact Ngeom:Nint pairs, e.g. 48000:48000"),
        ])
        mf = QGroupBox("Max Fourier mode")
        mfl = QHBoxLayout(mf)
        c_mf = QCheckBox("Override")
        sp_mf = QSpinBox()
        sp_mf.setRange(1, 500)
        sp_mf.setValue(30)
        mfl.addWidget(c_mf)
        mfl.addWidget(sp_mf)
        self.w["__mf_chk"] = c_mf
        self.w["__mf_sp"] = sp_mf
        il.addWidget(mf)
        add_form("Physics", [
            ("Contact model", "combo", ["legacy", "barrier_flat_at_rc"]),
            ("Root selection", "combo", ["continuation", "closest_to_a_nc", "lowest_energy", "targeted_x_nc"]),
            ("Branch mode", "combo", ["closest_to_a_nc", "lowest_energy"]),
            ("Emit v5 logs", "chk", True),
            ("Run v6 shiftfree postcheck", "chk", True),
        ])
        add_form("Build", [
            ("No torch", "chk", False),
            ("No local sst core", "chk", False),
            ("No auto compile", "chk", False),
            ("sstcore cmake build", "chk", False),
            ("SST project root", "line", str(_SST)),
            ("CMake build dir", "line", ""),
            ("CMake config", "line", "Release"),
        ])
        add_form("Extrapolation / archives", [
            ("Extrap min N_int", "spin", (0, 1_000_000, 8000)),
            ("No v8 extrapolation", "chk", False),
            ("No raw scan archive", "chk", False),
            ("No root candidate archive", "chk", False),
            ("No master batch archive", "chk", False),
        ])
        og = QGroupBox("Output / logging")
        of = QFormLayout(og)
        hr = QHBoxLayout()
        oute = QLineEdit(str(TREFOIL / "exports" / "sst_knot_v10_3_gui_run"))
        b = QPushButton("Browse…")
        b.clicked.connect(lambda: self._br(oute))
        hr.addWidget(oute)
        hr.addWidget(b)
        ww = QWidget()
        ww.setLayout(hr)
        of.addRow("Output dir:", ww)
        self.w["__out"] = oute
        c_ncl = QCheckBox("No console log file")
        of.addRow(c_ncl)
        self.w["__nocon"] = c_ncl
        cle = QLineEdit("")
        cle.setPlaceholderText("optional --console-log path")
        of.addRow("Console log path:", cle)
        self.w["__conlog"] = cle
        il.addWidget(og)
        br = QHBoxLayout()
        r1 = QPushButton("Run sweep")
        r1.setStyleSheet("background:#0055ff;color:white;font-weight:bold;padding:8px;")
        r1.clicked.connect(self.start)
        s1 = QPushButton("Stop")
        s1.setEnabled(False)
        s1.clicked.connect(self.stop)
        self._rb, self._sb = r1, s1
        o1 = QPushButton("Open output")
        o1.clicked.connect(self.open_out)
        c1 = QPushButton("Copy argv preview")
        c1.clicked.connect(self.copy_cmd)
        br.addWidget(r1)
        br.addWidget(s1)
        br.addWidget(o1)
        br.addWidget(c1)
        il.addLayout(br)
        il.addStretch()
        sc.setWidget(iw)
        L.addWidget(sc, 38)
        sp = QSplitter(Qt.Horizontal)
        st_scroll = QScrollArea()
        st_scroll.setWidgetResizable(True)
        st_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        pw = QWidget()
        pl = QVBoxLayout(pw)
        pl.addWidget(QLabel("Live status"))
        status_titles = [
            ("backend", "Backend"),
            ("knot_id", "Knot / batch"),
            ("ideal_source", "Ideal source"),
            ("local_sst_core", "Local sst_core"),
            ("A_req", "A_req"),
            ("latest_A_K", "Latest A_K"),
            ("latest_A_ratio", "Latest A/A_req"),
            ("latest_a_nc_over_rc", "Latest a_nc/r_c"),
            ("latest_a_star_over_rc", "Latest a*/r_c"),
            ("closure_x", "closure_x"),
            ("closure_x_minus_1", "closure_x − 1"),
            ("contact_model", "Contact model"),
            ("contact_force_at_x1", "C(1)"),
            ("F_at_x1", "F(1)"),
            ("continuation_jump", "Continuation jump"),
            ("latest_N_geom", "Latest N_geom"),
            ("latest_N_int", "Latest N_int"),
            ("elapsed_hint", "Elapsed (hint)"),
        ]
        for k, t in status_titles:
            c = StatusCard(t)
            self.cards[k] = c
            pl.addWidget(c)
        pl.addStretch()
        st_scroll.setWidget(pw)
        sp.addWidget(st_scroll)
        te = QPlainTextEdit()
        te.setReadOnly(True)
        te.setFont(QFont("Consolas", 10))
        te.setStyleSheet("QPlainTextEdit{background:#111317;color:#d6d9df;border:1px solid #2d3340;}")
        tw = QWidget()
        tl = QVBoxLayout(tw)
        tl.addWidget(QLabel("Raw log"))
        tl.addWidget(te)
        self.term = te
        sp.addWidget(tw)
        self.web_m = self.web_t = None
        if _WEB:
            tb = QTabWidget()
            self.web_m = QWebEngineView()
            self.web_m.setHtml(
                build_html_shell(
                    FORMULAS_MONITOR,
                    "Monitor ready",
                    "Parsed [FIT], [META], [BACKEND], … appear here with KaTeX.",
                )
            )
            self.web_t = QWebEngineView()
            self.web_t.setHtml(
                build_html_shell(
                    FORMULAS_THEOREM,
                    "Theorem / barrier tab",
                    "[THEOREM], [CHECK], [CONT], [BARRIER] stream here.",
                )
            )
            tb.addTab(self.web_m, "Monitor (KaTeX)")
            tb.addTab(self.web_t, "Theorem / barrier")
            sp.addWidget(tb)
        else:
            sp.addWidget(
                QLabel(
                    "PyQtWebEngine not available — structured KaTeX view disabled.\n"
                    "Raw log still works; install PyQtWebEngine for formula cards."
                )
            )
        sp.setSizes([220, 400, 480])
        L.addWidget(sp, 62)

    def _br(self, le: QLineEdit):
        p = QFileDialog.getExistingDirectory(self, "Output", le.text())
        if p:
            le.setText(p)

    def _gw(self, label: str):
        return self.w[label]

    def cmd(self) -> List[str]:
        o = Path(self.w["__out"].text().strip()).resolve()
        o.mkdir(parents=True, exist_ok=True)
        c = [sys.executable, "-u", str(SCRIPT), "--output-dir", str(o)]
        c += ["--mode", self._gw("Mode").currentText()]
        c += ["--preset", self._gw("Preset").currentText()]
        c += ["--backend", self._gw("Backend").currentText()]
        c += ["--sweep-layout", self._gw("Sweep layout").currentText()]
        c += ["--parallel-scope", self._gw("Parallel scope").currentText()]
        c += ["--max-workers", str(self._gw("Max workers (0=auto)").value())]
        c += ["--external-knotlib", self._gw("External knotlib").currentText()]
        kp, kl = self._gw("Knot preset").text().strip(), self._gw("Knot list").text().strip()
        if kp:
            c += ["--knot-preset", kp]
        if kl:
            c += ["--knot-list", kl]
        if not kp and not kl:
            c += ["--knot-id", self._gw("Knot id").text().strip() or "3:1:1"]
        if self.w["__mf_chk"].isChecked():
            c += ["--max-fourier-mode", str(self.w["__mf_sp"].value())]
        for lab, flag in [("N geom list", "--n-geom-list"), ("N int list", "--n-int-list"),
                          ("Lambda list", "--lambda-list"), ("Plateau fracs", "--plateau-fracs"),
                          ("Extra target pairs", "--extra-target-pairs")]:
            t = self._gw(lab).text().strip()
            if t:
                c += [flag, t]
        c += ["--contact-model", self._gw("Contact model").currentText()]
        c += ["--root-selection-mode", self._gw("Root selection").currentText()]
        c += ["--branch-mode", self._gw("Branch mode").currentText()]
        c += ["--emit-v5-logs", "1" if self._gw("Emit v5 logs").isChecked() else "0"]
        c += ["--run-v6-shiftfree-postcheck", "1" if self._gw("Run v6 shiftfree postcheck").isChecked() else "0"]
        c += ["--extrap-min-nint", str(self._gw("Extrap min N_int").value())]
        if self._gw("No torch").isChecked():
            c.append("--no-torch")
        if self._gw("No local sst core").isChecked():
            c.append("--no-local-sst-core")
        if self._gw("No auto compile").isChecked():
            c.append("--no-auto-compile")
        if self._gw("sstcore cmake build").isChecked():
            c.append("--sstcore-cmake-build")
        sr = self._gw("SST project root").text().strip()
        if sr:
            c += ["--sst-project-root", sr]
        cd = self._gw("CMake build dir").text().strip()
        if cd:
            c += ["--sst-cmake-build-dir", cd]
        cc = self._gw("CMake config").text().strip()
        if cc:
            c += ["--sst-cmake-config", cc]
        if self._gw("No v8 extrapolation").isChecked():
            c.append("--no-v8-extrapolation")
        if self._gw("No raw scan archive").isChecked():
            c.append("--no-raw-scan-archive")
        if self._gw("No root candidate archive").isChecked():
            c.append("--no-root-candidate-archive")
        if self._gw("No master batch archive").isChecked():
            c.append("--no-master-batch-archive")
        if self.w["__nocon"].isChecked():
            c.append("--no-console-log")
        cl = self.w["__conlog"].text().strip()
        if cl and not self.w["__nocon"].isChecked():
            c += ["--console-log", cl]
        return c

    def open_out(self):
        p = Path(self.w["__out"].text().strip()).resolve()
        p.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(p)))

    def copy_cmd(self):
        from PyQt5.QtWidgets import QApplication

        QApplication.clipboard().setText(subprocess.list2cmdline(self.cmd()))

    def _argv_flags_for_parser(self) -> List[str]:
        """CLI flags only (after ``python -u script``), for ``parse_args``."""
        full = self.cmd()
        return full[3:] if len(full) > 3 else []

    def _validate_argv(self) -> Optional[str]:
        """Validate against ``build_robustness_arg_parser()`` from the sweep module."""
        try:
            build_parser = _get_build_robustness_arg_parser()
        except Exception as exc:
            return f"Could not load sweep parser (validation skipped): {exc}"
        parser = build_parser()
        flags = self._argv_flags_for_parser()
        if hasattr(parser, "exit_on_error"):
            parser.exit_on_error = False  # type: ignore[assignment]
        try:
            parser.parse_args(flags)
        except SystemExit:
            return "Invalid CLI arguments (check choices and required formats)."
        except Exception as exc:
            return str(exc)
        return None

    def _append_web_event(self, web: Optional[Any], payload: dict) -> None:
        if not web:
            return
        js = (
            "appendEvent("
            + json.dumps(str(payload.get("kind", "info")))
            + ","
            + json.dumps(str(payload.get("title", "")))
            + ","
            + json.dumps(str(payload.get("body", "")))
            + ","
            + json.dumps(str(payload.get("raw", "")))
            + ","
            + json.dumps(str(payload.get("meta", "")))
            + ");"
        )
        web.page().runJavaScript(js)
        for key, value in payload.get("values", {}).items():
            if key in self.cards:
                self.cards[key].setv(str(value))

    def start(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Busy", "Already running.")
            return
        err = self._validate_argv()
        if err and not err.startswith("Could not load sweep parser"):
            QMessageBox.warning(self, "Invalid arguments", err)
            return
        self.term.clear()
        for x in self.cards.values():
            x.setv("")
        self.worker = ProcessWorker(self.cmd(), TREFOIL)
        self.worker.line_signal.connect(lambda ln: (self.term.appendPlainText(ln.rstrip("\n")),
            self.term.verticalScrollBar().setValue(self.term.verticalScrollBar().maximum())))
        self.worker.mon_signal.connect(lambda d: self._append_web_event(self.web_m, d))
        self.worker.th_signal.connect(lambda d: self._append_web_event(self.web_t, d))
        self.worker.state_signal.connect(self._st)
        self.worker.start()

    def _st(self, s: str):
        if s == "starting":
            self._rb.setEnabled(False)
            self._sb.setEnabled(True)
        elif s.startswith("finished"):
            self._rb.setEnabled(True)
            self._sb.setEnabled(False)
            code = s.split(":", 1)[1] if ":" in s else "?"
            d = {
                "kind": "ok" if code == "0" else "warn",
                "title": "Run finished",
                "body": f"Exit code <b>{he(code)}</b>.",
                "raw": s,
                "meta": "process",
                "values": {},
            }
            self._append_web_event(self.web_m, d)
            self._append_web_event(self.web_t, d)

    def stop(self):
        if self.worker:
            self.worker.stop()