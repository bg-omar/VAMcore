#!/usr/bin/env python3
"""
SST Trefoil V4 GUI — Monitor for sst_ideal_trefoil_robustness_sweep_v4.py

PyQt5 desktop app: run the v4 sweep script as subprocess, show raw terminal output,
parse [META], [BACKEND], [GEOM], [SCAN], [FIT], [ROOT], [BEST], [TIME] and update
status cards; right panel shows KaTeX formulas and parsed event cards.
"""

import json
import os
import re
import subprocess
import sys
import html as html_module

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QComboBox,
    QPlainTextEdit,
    QGroupBox,
    QFrame,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QFont, QTextCursor

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_SCRIPT = os.path.join(SCRIPT_DIR, "sst_ideal_trefoil_robustness_sweep_v4.py")
DEFAULT_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "sst_ideal_trefoil_robustness_outputs_v4")


def escape_html(text: str) -> str:
    return html_module.escape(str(text)).replace("\n", "<br>\n")


# -----------------------------------------------------------------------------
# KaTeX + formulas HTML template
# -----------------------------------------------------------------------------
KATEX_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"
    onload="renderMathInElement(document.body, {delimiters: [{left: '$$', right: '$$', display: true}, {left: '$', right: '$', display: false}]});"></script>
  <style>
    body { background-color: #1e1e1e; color: #d4d4d4; font-family: 'Consolas', monospace; font-size: 13px; padding: 12px; }
    .formula-block { margin: 12px 0; padding: 8px; border-left: 3px solid #4a9; }
    .card { margin: 8px 0; padding: 8px; background: #2d2d2d; border-radius: 4px; border: 1px solid #444; }
    .card-title { font-weight: bold; color: #8cf; }
    .card-raw { font-size: 11px; color: #888; margin-top: 4px; }
    .card-desc { margin-top: 4px; color: #b4b4b4; }
    #events { max-height: 400px; overflow-y: auto; }
  </style>
</head>
<body>
  <h3 style="color: #8cf;">SST closure formulas</h3>
  <div class="formula-block">Fourier curve: $X(t) = \\sum_k [A_k \\cos(2\\pi k t) + B_k \\sin(2\\pi k t)]$</div>
  <div class="formula-block">$E_{\\mathrm{BS}}(a)$ scan (Biot–Savart cutoff energy vs radius $a$)</div>
  <div class="formula-block">$A_K$ from local slope of $E_{\\mathrm{BS}}/L_K$ vs $-\\ln a$</div>
  <div class="formula-block">$a_{\\mathrm{nc}} = \\sqrt{A_K/\\pi}\\,\\Gamma_0/\\mathbf{v}_{\\!\\circlearrowright}$</div>
  <div class="formula-block">$E_K(a)$ = BS + core + contact terms; $a^* = \\arg\\min E_K(a)$</div>
  <div class="formula-block">$A_{\\mathrm{req}} = 1/(4\\pi)$</div>
  <h3 style="color: #8cf; margin-top: 20px;">Parsed events</h3>
  <div id="events"></div>
  <script>
    function appendCard(title, raw, desc) {
      const div = document.createElement('div');
      div.className = 'card';
      div.innerHTML = '<div class="card-title">' + title + '</div>' +
        (raw ? '<div class="card-raw">' + raw + '</div>' : '') +
        (desc ? '<div class="card-desc">' + desc + '</div>' : '');
      document.getElementById('events').appendChild(div);
      renderMathInElement(div, {delimiters: [{left: '$$', right: '$$', display: true}, {left: '$', right: '$', display: false}]});
      document.getElementById('events').scrollTop = document.getElementById('events').scrollHeight;
    }
  </script>
</body>
</html>
"""


def parse_log_line(line: str) -> tuple:
    """
    Parse a line with prefix [META], [BACKEND], [GEOM], [SCAN], [FIT], [ROOT], [BEST], [TIME], [WARN], [ERROR].
    Returns (prefix, rest, dict of parsed key=value for known prefixes).
    """
    line = line.strip()
    if not line.startswith("["):
        return None, line, {}
    match = re.match(r"^\[(\w+)\]\s*(.*)$", line)
    if not match:
        return None, line, {}
    prefix, rest = match.group(1), match.group(2)
    out = {}
    if prefix == "FIT":
        # [FIT] N_geom=16000 N_int=16000 method=plateau_0.12 A_K=0.07934203 A_ratio=0.997041 a_nc_over_rc=0.998520
        for part in rest.split():
            if "=" in part:
                k, v = part.split("=", 1)
                try:
                    out[k] = float(v)
                except ValueError:
                    out[k] = v
        out["_raw"] = rest
    elif prefix == "BACKEND":
        # [BACKEND] bs_backend=local_cpp_scan
        for part in rest.split():
            if "=" in part:
                k, v = part.split("=", 1)
                out[k] = v
        out["_raw"] = rest
    elif prefix == "BEST":
        for part in rest.split():
            if "=" in part:
                k, v = part.split("=", 1)
                try:
                    out[k] = float(v)
                except ValueError:
                    out[k] = v
        out["_raw"] = rest
    elif prefix == "TIME":
        for part in rest.split():
            if "=" in part:
                k, v = part.split("=", 1)
                try:
                    out[k] = float(v)
                except ValueError:
                    out[k] = v
        out["_raw"] = rest
    elif prefix in ("META", "GEOM", "SCAN", "ROOT", "WARN", "ERROR"):
        out["_raw"] = rest
    return prefix, rest, out


def card_interpretation(prefix: str, parsed: dict) -> str:
    """One-sentence interpretation for the rich panel."""
    if prefix == "FIT":
        A_K = parsed.get("A_K")
        A_req = 1.0 / (4.0 * 3.141592653589793)
        if A_K is not None:
            if abs(A_K - A_req) / A_req < 0.01:
                return "A_K is within 1% of 1/(4π) (closure target)."
            if A_K < A_req:
                return "A_K below 1/(4π); approaching from below."
            return "A_K above 1/(4π)."
    if prefix == "BACKEND":
        backend = parsed.get("bs_backend", "")
        if backend == "local_cpp_scan":
            return "Using local C++ Biot–Savart scan (fastest)."
        if backend == "torch":
            return "Using PyTorch-accelerated Biot–Savart."
        if backend == "numpy":
            return "Using NumPy Biot–Savart (no acceleration)."
    if prefix == "TIME":
        return "Timing for this phase."
    if prefix == "BEST":
        return "Current best-estimate (practical) from preferred no-contact run."
    if prefix == "GEOM":
        return "Geometry build completed."
    if prefix == "SCAN":
        return "Biot–Savart scan completed."
    if prefix == "ROOT":
        return "Root/minimizer for regularized model."
    return ""


# -----------------------------------------------------------------------------
# (No worker thread: we use QProcess in main window for async run)
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Main window
# -----------------------------------------------------------------------------
class SSTTrefoilV4Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SST Trefoil V4 — Robustness Sweep Monitor")
        self.resize(1280, 800)
        self.process = None
        self.output_dir = DEFAULT_OUTPUT_DIR

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # ----- Top control bar -----
        top = QHBoxLayout()
        top.addWidget(QLabel("Script:"))
        self.script_edit = QLineEdit(DEFAULT_SCRIPT)
        self.script_edit.setMinimumWidth(320)
        top.addWidget(self.script_edit)
        top.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["fast", "full"])
        top.addWidget(self.preset_combo)
        top.addWidget(QLabel("Backend:"))
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(["auto", "local_cpp_scan", "torch", "numpy"])
        top.addWidget(self.backend_combo)
        top.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["ideal", "torus"])
        top.addWidget(self.mode_combo)
        top.addWidget(QLabel("Output dir:"))
        self.output_edit = QLineEdit(DEFAULT_OUTPUT_DIR)
        self.output_edit.setMinimumWidth(280)
        top.addWidget(self.output_edit)
        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.start_run)
        top.addWidget(self.run_btn)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_run)
        self.stop_btn.setEnabled(False)
        top.addWidget(self.stop_btn)
        self.open_dir_btn = QPushButton("Open output folder")
        self.open_dir_btn.clicked.connect(self.open_output_folder)
        top.addWidget(self.open_dir_btn)
        layout.addLayout(top)

        # ----- Content: left status | center terminal | right rich -----
        content = QHBoxLayout()
        # Left status panel
        left = QFrame()
        left.setFrameStyle(QFrame.StyledPanel)
        left.setMaximumWidth(260)
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Status"))
        self.status_labels = {}
        for key in ("backend", "knot_id", "ideal_source", "local_sst_core", "A_req",
                    "A_K", "A_ratio", "a_nc_over_rc", "a_star_over_rc", "N_geom", "N_int", "elapsed"):
            lbl = QLabel("—")
            lbl.setWordWrap(True)
            self.status_labels[key] = lbl
            left_layout.addWidget(QLabel(key.replace("_", " ").title() + ":"))
            left_layout.addWidget(lbl)
        left_layout.addStretch()
        content.addWidget(left)

        # Center terminal
        self.terminal = QPlainTextEdit()
        self.terminal.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas; font-size: 12px;")
        self.terminal.setPlaceholderText("Output from sweep script will appear here…")
        self.terminal.setReadOnly(True)
        content.addWidget(self.terminal, stretch=1)

        # Right rich panel (formulas + events)
        self.web = QWebEngineView()
        self.web.setHtml(KATEX_HTML_TEMPLATE)
        content.addWidget(self.web, stretch=1)

        layout.addLayout(content)

        # ----- Output artifact panel -----
        artifact = QHBoxLayout()
        artifact.addWidget(QLabel("Output files:"))
        self.csv_btn = QPushButton("CSV summary")
        self.csv_btn.clicked.connect(lambda: self._open_artifact("robustness_summary_v4_ideal.csv"))
        self.best_csv_btn = QPushButton("Best-estimate CSV")
        self.best_csv_btn.clicked.connect(lambda: self._open_artifact("final_best_estimate_v4.csv"))
        self.best_txt_btn = QPushButton("Best-estimate TXT")
        self.best_txt_btn.clicked.connect(lambda: self._open_artifact("final_best_estimate_v4.txt"))
        artifact.addWidget(self.csv_btn)
        artifact.addWidget(self.best_csv_btn)
        artifact.addWidget(self.best_txt_btn)
        artifact.addStretch()
        layout.addLayout(artifact)

        self.run_start_time = None

    def _open_artifact(self, name: str):
        path = os.path.join(self.output_dir, name)
        if os.path.isfile(path):
            if sys.platform == "win32":
                os.startfile(path)
            else:
                subprocess.run(["xdg-open", path], check=False)
        else:
            QMessageBox.information(self, "File not found", "File not yet created: " + name)

    def open_output_folder(self):
        d = self.output_edit.text().strip() or DEFAULT_OUTPUT_DIR
        if not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(d)
        else:
            subprocess.run(["xdg-open", d], check=False)

    def start_run(self):
        script = self.script_edit.text().strip()
        if not os.path.isfile(script):
            QMessageBox.warning(self, "Script not found", "Script not found: " + script)
            return
        self.output_dir = self.output_edit.text().strip() or DEFAULT_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        preset = self.preset_combo.currentText()
        backend = self.backend_combo.currentText()
        mode = self.mode_combo.currentText()
        args = ["--preset", preset, "--backend", backend, "--mode", mode, "--output-dir", self.output_dir]
        cwd = os.path.dirname(script) or SCRIPT_DIR
        self.terminal.clear()
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.run_start_time = __import__("time").perf_counter()
        for k, lbl in self.status_labels.items():
            lbl.setText("—")
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        self.process = QProcess(self)
        self.process.setWorkingDirectory(cwd)
        from PyQt5.QtCore import QProcessEnvironment
        penv = QProcessEnvironment.systemEnvironment()
        for k, v in env.items():
            penv.insert(k, str(v))
        self.process.setProcessEnvironment(penv)
        cmd = [sys.executable, "-u", script] + args
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.readyReadStandardError.connect(self._on_stderr)
        self.process.finished.connect(self._on_process_finished)
        self.process.start(cmd[0], cmd[1:])

    def _on_stdout(self):
        if self.process is None:
            return
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        for line in data.splitlines():
            self.on_line(line)

    def _on_stderr(self):
        if self.process is None:
            return
        data = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        for line in data.splitlines():
            self.terminal.appendPlainText(line)
            self.terminal.verticalScrollBar().setValue(self.terminal.verticalScrollBar().maximum())

    def _on_process_finished(self, code: int, status):
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        elapsed = __import__("time").perf_counter() - self.run_start_time if self.run_start_time else 0
        self.status_labels["elapsed"].setText("{:.1f} s (exit {})".format(elapsed, code))
        self.process = None

    def stop_run(self):
        if self.process and self.process.state() == QProcess.Running:
            self.process.terminate()
            self.process.waitForFinished(3000)
            if self.process and self.process.state() == QProcess.Running:
                self.process.kill()

    def on_line(self, line: str):
        self.terminal.appendPlainText(line)
        self.terminal.verticalScrollBar().setValue(self.terminal.verticalScrollBar().maximum())
        prefix, rest, parsed = parse_log_line(line)
        if prefix is None:
            return
        # Update status cards
        if prefix == "BACKEND" and "bs_backend" in parsed:
            self.status_labels["backend"].setText(parsed["bs_backend"])
        if prefix == "FIT":
            if "N_geom" in parsed:
                self.status_labels["N_geom"].setText(str(int(parsed["N_geom"])))
            if "N_int" in parsed:
                self.status_labels["N_int"].setText(str(int(parsed["N_int"])))
            if "A_K" in parsed:
                self.status_labels["A_K"].setText("{:.6f}".format(parsed["A_K"]))
            if "A_ratio" in parsed:
                self.status_labels["A_ratio"].setText("{:.6f}".format(parsed["A_ratio"]))
            if "a_nc_over_rc" in parsed:
                self.status_labels["a_nc_over_rc"].setText("{:.6f}".format(parsed["a_nc_over_rc"]))
        if prefix == "BEST":
            if "A_K" in parsed:
                self.status_labels["A_K"].setText("{:.6f}".format(parsed["A_K"]))
            if "A_ratio" in parsed:
                self.status_labels["A_ratio"].setText("{:.6f}".format(parsed["A_ratio"]))
            if "a_nc_over_rc" in parsed:
                self.status_labels["a_nc_over_rc"].setText("{:.6f}".format(parsed["a_nc_over_rc"]))
            if "a_star_over_rc" in parsed:
                self.status_labels["a_star_over_rc"].setText("{:.6f}".format(parsed["a_star_over_rc"]))
        if prefix == "META" and "ideal_source=" in rest:
            idx = rest.find("ideal_source=")
            val = rest[idx + 13:].strip() if idx >= 0 else ""
            self.status_labels["ideal_source"].setText(val[:50] + "…" if len(val) > 50 else val)
        if prefix == "TIME" and "total_script_s" in parsed:
            self.status_labels["elapsed"].setText("{:.1f} s".format(parsed.get("total_script_s", 0)))
        # Defaults for display
        self.status_labels["A_req"].setText("{:.6f}".format(1.0 / (4.0 * 3.141592653589793)))
        self.status_labels["knot_id"].setText("3:1:1")
        self.status_labels["local_sst_core"].setText("—")
        # Append card to rich panel (escape for JS)
        title = prefix
        raw = escape_html(rest[:200] + ("…" if len(rest) > 200 else ""))
        desc = escape_html(card_interpretation(prefix, parsed))
        js = "appendCard({}, {}, {});".format(
            json.dumps(title),
            json.dumps(raw),
            json.dumps(desc),
        )
        self.web.page().runJavaScript(js)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = SSTTrefoilV4Window()
    w.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
