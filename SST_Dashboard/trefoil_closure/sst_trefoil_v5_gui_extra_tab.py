#!/usr/bin/env python3
"""
SST trefoil v5 GUI monitor (fixed)
----------------------------------
Adds a dedicated theorem / continuation tab on top of the v4 monitor.

Tab 1: live formulas + structured run events
Tab 2: theorem / continuation diagnostics for proving a*/r_c
"""
from __future__ import annotations

import html
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

from PyQt5.QtCore import QThread, pyqtSignal, Qt, QUrl
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SCRIPT = SCRIPT_DIR / "sst_ideal_trefoil_robustness_sweep_v5.py"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "exports/sst_ideal_trefoil_robustness_outputs_v5"

FORMULAS_MONITOR = [
    ("Fourier curve", r"X(t)=\sum_k\left[A_k\cos(2\pi k t)+B_k\sin(2\pi k t)\right]"),
    ("Biot--Savart scan", r"E_{BS}(a)\;\text{sampled over cutoff}\; a"),
    ("Slope extraction", r"A_K\approx \frac{d(E_{BS}/L_K)}{d(-\ln a)}"),
    ("No-contact radius", r"a_{\mathrm{nc}}=\sqrt{A_K/\pi}\,\Gamma_0/\mathbf{v}_{\!\boldsymbol{\circlearrowleft}}"),
    ("Regularized energy", r"E_K(a)=E_{BS}(a)+E_{\mathrm{core}}(a)+E_{\mathrm{contact}}(a)"),
    ("Selected minimum", r"a^*=\arg\min E_K(a)"),
    ("Closure benchmark", r"A_{\mathrm{req}}=\frac{1}{4\pi}"),
]

FORMULAS_THEOREM = [
    ("No-contact theorem target", r"\frac{a_{\mathrm{nc}}}{r_c}=\sqrt{4\pi A_K}"),
    ("Dimensionless stationarity", r"F(x)=x-\frac{4\pi A_K}{x}+C_{\lambda,p}(x;\beta)=0,\quad x=\frac{a}{r_c}"),
    ("Exact full-model closure", r"a^*=r_c\iff F(1)=0"),
    ("Barrier-flat condition", r"\left.\frac{dE_{\mathrm{cont}}}{da}\right|_{a=r_c}=0"),
    ("Continuation rule", r"a^*(\lambda_{n+1})\leftarrow \operatorname*{argmin}_{\text{same branch}} |a-a^*(\lambda_n)|"),
    ("Closure residual", r"\Delta_{\mathrm{closure}}=\sqrt{4\pi A_K}-1"),
]

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
CHECK_RE = re.compile(r"\[CHECK\].*method=(?P<method>[^\s]+).*closure_x=(?P<closure_x>[-+0-9.eE]+).*closure_x_minus_1=(?P<delta>[-+0-9.eE]+)")
CONT_RE = re.compile(r"\[CONT\].*lambda_K=(?P<lam>[-+0-9.eE]+).*prev_a_star_over_rc=(?P<prev>[^\s]+).*a_star_over_rc=(?P<curr>[-+0-9.eE]+).*jump=(?P<jump>[^\s]+).*root_choice=(?P<choice>[^\s]+)")
BARRIER_RE = re.compile(r"\[BARRIER\].*lambda_K=(?P<lam>[-+0-9.eE]+).*beta=(?P<beta>[-+0-9.eE]+).*contact_force_at_x1=(?P<cf>[-+0-9.eE]+).*F_at_x1=(?P<Fx1>[-+0-9.eE]+).*contact_model=(?P<model>[^\s]+)")
PATH_RE = re.compile(r"(?P<path>[A-Za-z]:\\[^\n]+|/[^\n]+\.(?:csv|txt|tex|png|json))")


def html_escape(text: str) -> str:
    return html.escape(text, quote=True)


def _formula_cards(formulas):
    return "".join(
        f"<div class='formula-card'><div class='formula-title'>{html_escape(title)}</div><div class='formula-body'>$$ {latex} $$</div></div>"
        for title, latex in formulas
    )


def build_html_shell(formulas, initial_title, initial_meta):
    formula_html = _formula_cards(formulas)
    return f"""
<!DOCTYPE html>
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
    <div class="section-title">SST formulas in use</div>
    <div id="formula-grid">{formula_html}</div>
  </div>
  <div>
    <div class="section-title">Structured events</div>
    <div id="events">
      <div class="event-card info"><div class="event-title">{html_escape(initial_title)}</div><div class="event-meta">{html_escape(initial_meta)}</div></div>
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
  const events = document.getElementById('events');
  events.prepend(card);
  renderMath(card);
}}
</script>
</body>
</html>
"""


class ProcessWorker(QThread):
    line_signal = pyqtSignal(str)
    monitor_event_signal = pyqtSignal(dict)
    theorem_event_signal = pyqtSignal(dict)
    state_signal = pyqtSignal(str)

    def __init__(self, command: List[str], cwd: Path):
        super().__init__()
        self.command = command
        self.cwd = cwd
        self.proc: Optional[subprocess.Popen] = None
        self._stop_requested = False

    def stop(self) -> None:
        self._stop_requested = True
        if self.proc is None:
            return
        try:
            if os.name == "nt":
                self.proc.terminate()
            else:
                self.proc.send_signal(signal.SIGTERM)
        except Exception:
            pass

    def _emit_monitor(self, payload: dict) -> None:
        self.monitor_event_signal.emit(payload)

    def _emit_theorem(self, payload: dict) -> None:
        self.theorem_event_signal.emit(payload)

    def _emit_parsed(self, line: str) -> None:
        line = line.rstrip("\n")
        m = FIT_RE.search(line)
        if m:
            A_ratio = float(m.group("A_ratio"))
            body = (
                f"Method <b>{html_escape(m.group('method'))}</b> at $N_{{\\mathrm{{geom}}}}={m.group('N_geom')}$, "
                f"$N_{{\\mathrm{{int}}}}={m.group('N_int')}$ gives "
                f"$A_K={float(m.group('A_K')):.8f}$, "
                f"$A_K/A_{{\\mathrm{{req}}}}={A_ratio:.6f}$, "
                f"$a_{{\\mathrm{{nc}}}}/r_c={float(m.group('a_nc')):.6f}$."
            )
            kind = "ok" if abs(A_ratio - 1.0) < 0.01 else ("info" if abs(A_ratio - 1.0) < 0.05 else "warn")
            payload = {
                "kind": kind,
                "title": "Fit update",
                "body": body,
                "raw": line,
                "meta": f"method={m.group('method')}",
                "values": {
                    "latest_A_K": f"{float(m.group('A_K')):.8f}",
                    "latest_A_ratio": f"{A_ratio:.6f}",
                    "latest_a_nc_over_rc": f"{float(m.group('a_nc')):.6f}",
                    "latest_N_geom": m.group("N_geom"),
                    "latest_N_int": m.group("N_int"),
                },
            }
            self._emit_monitor(payload)
            return
        m = BACKEND_RE.search(line)
        if m:
            backend = m.group("backend")
            explain = {
                "local_cpp_scan": "Local C++ cutoff scan is active.",
                "torch": "PyTorch acceleration is active.",
                "numpy": "Pure NumPy path is active; slow but reference-safe.",
            }.get(backend, "Backend selected.")
            self._emit_monitor({
                "kind": "info", "title": "Backend", "body": html_escape(explain), "raw": line, "meta": backend,
                "values": {"backend": backend},
            })
            return
        m = META_RE.search(line)
        if m:
            key = m.group("key").strip(); value = m.group("value").strip(); vals = {}
            lower = key.lower()
            if "knot" in lower:
                vals["knot_id"] = value
            elif "ideal source" in lower or "ideal_source" in lower:
                vals["ideal_source"] = value
            elif "local sst_core" in lower:
                vals["local_sst_core"] = value
            elif key.strip() == "A_req":
                vals["A_req"] = value
            self._emit_monitor({"kind": "info", "title": key, "body": html_escape(value), "raw": line, "meta": "metadata", "values": vals})
            return
        m = ROOT_RE.search(line)
        if m:
            self._emit_monitor({
                "kind": "info", "title": "Regularized minimum",
                "body": f"Latest selected branch gives $a^*/r_c={float(m.group('a_star')):.6f}$.",
                "raw": line, "meta": "root", "values": {"latest_a_star_over_rc": f"{float(m.group('a_star')):.6f}"},
            })
            return
        m = TIME_RE.search(line)
        if m:
            self._emit_monitor({
                "kind": "info", "title": f"Timing — {html_escape(m.group('label'))}",
                "body": f"Elapsed time: <b>{float(m.group('value')):.3f} s</b>.",
                "raw": line, "meta": "timing", "values": {"elapsed_hint": f"{float(m.group('value')):.3f} s"},
            })
            return
        m = BEST_RE.search(line)
        if m:
            self._emit_monitor({"kind": "ok", "title": "Best-estimate update", "body": html_escape(m.group('body')), "raw": line, "meta": "best", "values": {}})
            return
        m = THEOREM_RE.search(line)
        if m:
            self._emit_theorem({"kind": "info", "title": "Theorem target", "body": html_escape(m.group('body')), "raw": line, "meta": "theorem", "values": {}})
            return
        m = CHECK_RE.search(line)
        if m:
            delta = float(m.group('delta'))
            kind = 'ok' if abs(delta) < 1e-2 else ('info' if abs(delta) < 5e-2 else 'warn')
            self._emit_theorem({
                "kind": kind,
                "title": f"No-contact closure check — {html_escape(m.group('method'))}",
                "body": f"$x_{{\\mathrm{{closure}}}}=\\sqrt{{4\\pi A_K}}={float(m.group('closure_x')):.8f}$, so $x_{{\\mathrm{{closure}}}}-1={delta:.3e}$.",
                "raw": line,
                "meta": "closure_x",
                "values": {"closure_x": f"{float(m.group('closure_x')):.8f}", "closure_x_minus_1": f"{delta:.3e}"},
            })
            return
        m = CONT_RE.search(line)
        if m:
            jump_text = m.group('jump')
            try:
                jump = float(jump_text)
                kind = 'ok' if abs(jump) < 5e-3 else ('info' if abs(jump) < 2e-2 else 'warn')
            except Exception:
                jump = None
                kind = 'info'
            body = (
                f"At $\\lambda_K={float(m.group('lam')):.4g}$ the selected branch is "
                f"$a^*/r_c={float(m.group('curr')):.6f}$ using <b>{html_escape(m.group('choice'))}</b>."
            )
            if jump is not None:
                body += f" Branch jump diagnostic: $\\Delta={jump:.3e}$."
            self._emit_theorem({
                "kind": kind,
                "title": "Continuation step",
                "body": body,
                "raw": line,
                "meta": f"lambda={m.group('lam')}",
                "values": {"continuation_jump": jump_text, "latest_a_star_over_rc": f"{float(m.group('curr')):.6f}"},
            })
            return
        m = BARRIER_RE.search(line)
        if m:
            cf = float(m.group('cf')); Fx1 = float(m.group('Fx1'))
            kind = 'ok' if abs(cf) < 1e-8 and abs(Fx1) < 1e-2 else ('info' if abs(Fx1) < 5e-2 else 'warn')
            self._emit_theorem({
                "kind": kind,
                "title": "Barrier / full-model check",
                "body": (
                    f"Contact model <b>{html_escape(m.group('model'))}</b> at $\\lambda_K={float(m.group('lam')):.4g}$ gives "
                    f"$\\beta={float(m.group('beta')):.6f}$, "
                    f"$C(1)={cf:.3e}$, "
                    f"$F(1)={Fx1:.3e}$."
                ),
                "raw": line,
                "meta": "barrier",
                "values": {"contact_force_at_x1": f"{cf:.3e}", "F_at_x1": f"{Fx1:.3e}", "contact_model": m.group('model')},
            })
            return
        if line.startswith("[WARN]"):
            self._emit_monitor({"kind": "warn", "title": "Warning", "body": html_escape(line[6:].strip()), "raw": line, "meta": "warning", "values": {}})
            return
        if line.startswith("[ERROR]"):
            self._emit_monitor({"kind": "err", "title": "Error", "body": html_escape(line[7:].strip()), "raw": line, "meta": "error", "values": {}})
            self._emit_theorem({"kind": "err", "title": "Error", "body": html_escape(line[7:].strip()), "raw": line, "meta": "error", "values": {}})
            return

    def run(self) -> None:
        self.state_signal.emit("starting")
        env = os.environ.copy(); env.setdefault("PYTHONUNBUFFERED", "1")
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        self.proc = subprocess.Popen(
            self.command,
            cwd=str(self.cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env,
            creationflags=creationflags,
        )
        self.state_signal.emit("running")
        assert self.proc.stdout is not None
        for line in self.proc.stdout:
            self.line_signal.emit(line)
            self._emit_parsed(line)
            if self._stop_requested:
                break
        rc = self.proc.wait()
        self.state_signal.emit(f"finished:{rc}")


class StatusCard(QFrame):
    def __init__(self, title: str):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("QFrame { background:#20242c; border:1px solid #2d3340; border-radius:8px; } QLabel { color:#d8deeb; }")
        lay = QVBoxLayout(self); lay.setContentsMargins(10, 8, 10, 8)
        self.title_label = QLabel(title); self.title_label.setStyleSheet("font-weight:700; color:#8fb7ff;")
        self.value_label = QLabel("—"); self.value_label.setWordWrap(True); self.value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lay.addWidget(self.title_label); lay.addWidget(self.value_label)

    def set_value(self, text: str) -> None:
        self.value_label.setText(text if text else "—")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SST Trefoil v5 Monitor")
        self.resize(1700, 980)
        self.worker: Optional[ProcessWorker] = None
        self.run_started_at: Optional[float] = None

        central = QWidget(); self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.addLayout(self._build_controls())
        splitter = QSplitter(Qt.Horizontal); outer.addWidget(splitter, 1)
        splitter.addWidget(self._build_status_panel())
        splitter.addWidget(self._build_terminal_panel())
        splitter.addWidget(self._build_tabs_panel())
        splitter.setSizes([320, 620, 780])

    def _build_controls(self):
        layout = QGridLayout(); layout.setColumnStretch(7, 1)
        self.script_edit = QLineEdit(str(DEFAULT_SCRIPT))
        self.preset_combo = QComboBox(); self.preset_combo.addItems(["fast", "full"])
        self.backend_combo = QComboBox(); self.backend_combo.addItems(["auto", "local_cpp_scan", "torch", "numpy"])
        self.mode_combo = QComboBox(); self.mode_combo.addItems(["ideal", "torus"])
        self.contact_model_combo = QComboBox(); self.contact_model_combo.addItems(["legacy", "barrier_flat_at_rc"])
        self.root_mode_combo = QComboBox(); self.root_mode_combo.addItems(["continuation", "closest_to_a_nc", "lowest_energy"])
        self.output_edit = QLineEdit(str(DEFAULT_OUTPUT_DIR))
        self.extra_args_edit = QLineEdit("")
        self.extra_args_edit.setPlaceholderText("Extra CLI args, e.g. --knot-id 3:1:1 --max-fourier-mode 30")
        browse_script = QPushButton("Browse script"); browse_script.clicked.connect(self.browse_script)
        browse_out = QPushButton("Browse output"); browse_out.clicked.connect(self.browse_output)
        self.run_btn = QPushButton("Run"); self.run_btn.clicked.connect(self.start_run)
        self.stop_btn = QPushButton("Stop"); self.stop_btn.clicked.connect(self.stop_run); self.stop_btn.setEnabled(False)
        self.open_output_btn = QPushButton("Open output folder"); self.open_output_btn.clicked.connect(self.open_output_dir)

        row = 0
        layout.addWidget(QLabel("Script"), row, 0); layout.addWidget(self.script_edit, row, 1, 1, 5); layout.addWidget(browse_script, row, 6)
        row += 1
        layout.addWidget(QLabel("Preset"), row, 0); layout.addWidget(self.preset_combo, row, 1)
        layout.addWidget(QLabel("Backend"), row, 2); layout.addWidget(self.backend_combo, row, 3)
        layout.addWidget(QLabel("Mode"), row, 4); layout.addWidget(self.mode_combo, row, 5)
        row += 1
        layout.addWidget(QLabel("Contact model"), row, 0); layout.addWidget(self.contact_model_combo, row, 1)
        layout.addWidget(QLabel("Root mode"), row, 2); layout.addWidget(self.root_mode_combo, row, 3)
        row += 1
        layout.addWidget(QLabel("Output dir"), row, 0); layout.addWidget(self.output_edit, row, 1, 1, 5); layout.addWidget(browse_out, row, 6)
        row += 1
        layout.addWidget(QLabel("Extra args"), row, 0); layout.addWidget(self.extra_args_edit, row, 1, 1, 6)
        row += 1
        layout.addWidget(self.run_btn, row, 0); layout.addWidget(self.stop_btn, row, 1); layout.addWidget(self.open_output_btn, row, 2)
        return layout

    def _build_status_panel(self):
        panel = QWidget(); lay = QVBoxLayout(panel); lay.setContentsMargins(4, 4, 4, 4)
        lay.addWidget(QLabel("Live status"))
        titles = [
            ("backend", "Backend"), ("knot_id", "Knot ID"), ("ideal_source", "Ideal source"), ("local_sst_core", "Local sst_core"),
            ("A_req", "A_req"), ("latest_A_K", "Latest A_K"), ("latest_A_ratio", "Latest A/A_req"),
            ("latest_a_nc_over_rc", "Latest a_nc/r_c"), ("latest_a_star_over_rc", "Latest a*/r_c"),
            ("closure_x", "closure_x"), ("closure_x_minus_1", "closure_x - 1"), ("contact_model", "Contact model"),
            ("contact_force_at_x1", "C(1)"), ("F_at_x1", "F(1)"), ("continuation_jump", "Continuation jump"),
            ("latest_N_geom", "Latest N_geom"), ("latest_N_int", "Latest N_int"),
        ]
        self.cards: Dict[str, StatusCard] = {}
        for key, title in titles:
            card = StatusCard(title); self.cards[key] = card; lay.addWidget(card)
        lay.addStretch(1); return panel

    def _build_terminal_panel(self):
        panel = QWidget(); lay = QVBoxLayout(panel)
        self.terminal = QPlainTextEdit(); self.terminal.setReadOnly(True); self.terminal.setFont(QFont("Consolas", 10))
        self.terminal.setStyleSheet("QPlainTextEdit { background:#111317; color:#d6d9df; border:1px solid #2d3340; }")
        lay.addWidget(QLabel("Qt terminal (raw stdout/stderr)")); lay.addWidget(self.terminal, 1)
        return panel

    def _build_tabs_panel(self):
        panel = QWidget(); lay = QVBoxLayout(panel)
        self.tabs = QTabWidget()
        self.web_monitor = QWebEngineView(); self.web_monitor.setHtml(build_html_shell(FORMULAS_MONITOR, "GUI ready", "Waiting for run start."))
        self.web_theorem = QWebEngineView(); self.web_theorem.setHtml(build_html_shell(FORMULAS_THEOREM, "Theorem tab ready", "Waiting for v5 theorem / continuation logs."))
        self.tabs.addTab(self.web_monitor, "Monitor")
        self.tabs.addTab(self.web_theorem, "Proof / Continuation")
        lay.addWidget(self.tabs, 1)
        return panel

    def browse_script(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select script", str(SCRIPT_DIR), "Python (*.py)")
        if path:
            self.script_edit.setText(path)

    def browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "Select output directory", self.output_edit.text())
        if path:
            self.output_edit.setText(path)

    def open_output_dir(self):
        path = Path(self.output_edit.text()).resolve(); path.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def append_terminal(self, line: str):
        self.terminal.appendPlainText(line.rstrip("\n"))
        self.terminal.verticalScrollBar().setValue(self.terminal.verticalScrollBar().maximum())

    def _append_web_event(self, web: QWebEngineView, payload: dict):
        title = html_escape(str(payload.get("title", "Event")))
        body = str(payload.get("body", ""))
        raw = html_escape(str(payload.get("raw", "")))
        meta = html_escape(str(payload.get("meta", "")))
        kind = html_escape(str(payload.get("kind", "info")))
        js = "appendEvent(" + json.dumps(kind) + "," + json.dumps(title) + "," + json.dumps(body) + "," + json.dumps(raw) + "," + json.dumps(meta) + ");"
        web.page().runJavaScript(js)
        for key, value in payload.get("values", {}).items():
            if key in self.cards:
                self.cards[key].set_value(str(value))

    def append_monitor_event(self, payload: dict):
        self._append_web_event(self.web_monitor, payload)

    def append_theorem_event(self, payload: dict):
        self._append_web_event(self.web_theorem, payload)

    def set_state(self, state: str):
        if state == "starting":
            self.run_started_at = time.time(); self.run_btn.setEnabled(False); self.stop_btn.setEnabled(True)
        elif state.startswith("finished"):
            self.run_btn.setEnabled(True); self.stop_btn.setEnabled(False)
            code = state.split(":", 1)[1] if ":" in state else "?"
            payload = {"kind": "ok" if code == "0" else "warn", "title": "Run finished", "body": f"Exit code <b>{html_escape(code)}</b>.", "raw": state, "meta": "process", "values": {}}
            self.append_monitor_event(payload); self.append_theorem_event(payload)

    def build_command(self) -> List[str]:
        script = Path(self.script_edit.text()).resolve(); outdir = Path(self.output_edit.text()).resolve(); outdir.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable, "-u", str(script),
            "--preset", self.preset_combo.currentText(),
            "--backend", self.backend_combo.currentText(),
            "--mode", self.mode_combo.currentText(),
            "--contact-model", self.contact_model_combo.currentText(),
            "--root-selection-mode", self.root_mode_combo.currentText(),
            "--output-dir", str(outdir),
        ]
        extra = self.extra_args_edit.text().strip()
        if extra:
            cmd.extend(shlex.split(extra, posix=os.name != "nt"))
        return cmd

    def start_run(self):
        if self.worker is not None and self.worker.isRunning():
            QMessageBox.warning(self, "Run active", "A process is already running.")
            return
        script = Path(self.script_edit.text())
        if not script.exists():
            QMessageBox.critical(self, "Missing script", f"Script not found:\n{script}")
            return
        self.terminal.clear()
        self.worker = ProcessWorker(self.build_command(), script.parent)
        self.worker.line_signal.connect(self.append_terminal)
        self.worker.monitor_event_signal.connect(self.append_monitor_event)
        self.worker.theorem_event_signal.connect(self.append_theorem_event)
        self.worker.state_signal.connect(self.set_state)
        self.worker.start()

    def stop_run(self):
        if self.worker is not None:
            self.worker.stop()


def main() -> int:
    app = QApplication(sys.argv)
    win = MainWindow(); win.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())