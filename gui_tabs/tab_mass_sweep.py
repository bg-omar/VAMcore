# gui_tabs/tab_mass_sweep.py
# Mass Sweep tab: embedded ideal.txt, batch sweep with CSV export, GUI-friendly worker.

import os
import sys
import traceback
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QLineEdit, QProgressBar, QTextEdit, QGroupBox, QFileDialog, QMessageBox,
    QSpinBox, QDoubleSpinBox, QFormLayout, QScrollArea,
)
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, Qt

try:
    import swirl_string_core as sstcore
except ImportError:
    try:
        import sstbindings as sstcore
    except ImportError:
        sstcore = None

# Import sweep logic from examples (portable whether run from repo root or examples/)
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_examples = os.path.join(_root, "examples")
if _examples not in sys.path:
    sys.path.insert(0, _examples)
try:
    from master_sweep import run_master_sweep_embedded, parse_ideal_database_embedded
except ImportError:
    run_master_sweep_embedded = None
    parse_ideal_database_embedded = None


# =============================================================================
# Worker: run sweep in background thread
# =============================================================================
class MassSweepWorker(QObject):
    sig_log = pyqtSignal(str)
    sig_progress = pyqtSignal(int, int, str)   # done, total, current_id
    sig_finished = pyqtSignal(str)             # output_csv path
    sig_error = pyqtSignal(str)

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self._cancel = False

    @pyqtSlot()
    def run(self):
        if run_master_sweep_embedded is None:
            self.sig_error.emit("master_sweep.run_master_sweep_embedded not available.")
            return
        try:
            output_csv = self.config["output_csv"]

            def _log(msg):
                self.sig_log.emit(str(msg))

            def _progress(done, total, current_id):
                self.sig_progress.emit(int(done), int(total), str(current_id))

            def _cancel_check():
                return self._cancel

            run_master_sweep_embedded(
                output_csv=output_csv,
                embedded_name=self.config.get("embedded_name", "ideal.txt"),
                selected_ids=self.config.get("selected_ids", None),
                resolution_calibration=int(self.config.get("resolution_calibration", 1500)),
                relax_iterations_calibration=int(self.config.get("relax_iterations_calibration", 1500)),
                resolution_batch=int(self.config.get("resolution_batch", 1000)),
                relax_iterations_batch=int(self.config.get("relax_iterations_batch", 1200)),
                timestep=float(self.config.get("timestep", 0.005)),
                log_fn=_log,
                progress_fn=_progress,
                cancel_check=_cancel_check,
            )
            self.sig_finished.emit(output_csv)
        except Exception as e:
            self.sig_error.emit(f"{e}\n\n{traceback.format_exc()}")

    def cancel(self):
        self._cancel = True


# =============================================================================
# Tab UI
# =============================================================================
def _get_embedded_ab_ids(embedded_name="ideal.txt"):
    """Return list of (display_string, id) for combo. Uses embedded parser or empty."""
    if parse_ideal_database_embedded is None or sstcore is None:
        return []
    try:
        knots = parse_ideal_database_embedded(embedded_name)
        return [(f"{k['id']} (c={k['crossings']}, n={k['components']})", k["id"]) for k in knots]
    except Exception:
        return []


class TabMassSweep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # --- Scope & AB selection ---
        scope_group = QGroupBox("Sweep scope")
        scope_layout = QVBoxLayout(scope_group)
        scope_row = QHBoxLayout()
        scope_row.addWidget(QLabel("Scope:"))
        self.combo_sweep_scope = QComboBox()
        self.combo_sweep_scope.addItems(["All ABs (embedded ideal.txt)", "Selected AB only"])
        self.combo_sweep_scope.currentTextChanged.connect(self._on_scope_changed)
        scope_row.addWidget(self.combo_sweep_scope)
        scope_layout.addLayout(scope_row)

        scope_row2 = QHBoxLayout()
        scope_row2.addWidget(QLabel("AB (for 'Selected'):"))
        self.combo_ab = QComboBox()
        self._refresh_ab_combo()
        scope_row2.addWidget(self.combo_ab)
        self.btn_refresh_ab = QPushButton("Refresh list")
        self.btn_refresh_ab.clicked.connect(self._refresh_ab_combo)
        scope_row2.addWidget(self.btn_refresh_ab)
        scope_layout.addLayout(scope_row2)
        layout.addWidget(scope_group)

        # --- Parameters ---
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout(params_group)

        self.combo_res_cal = QComboBox()
        self.combo_res_cal.setEditable(True)
        self.combo_res_cal.addItems(["1000", "1500", "2000"])
        self.combo_res_cal.setCurrentText("1500")
        params_layout.addRow("Calibration resolution:", self.combo_res_cal)

        self.combo_relax_cal = QComboBox()
        self.combo_relax_cal.setEditable(True)
        self.combo_relax_cal.addItems(["1200", "1500", "2000"])
        self.combo_relax_cal.setCurrentText("1500")
        params_layout.addRow("Calibration relax iterations:", self.combo_relax_cal)

        self.combo_res_batch = QComboBox()
        self.combo_res_batch.setEditable(True)
        self.combo_res_batch.addItems(["800", "1000", "1200", "1500"])
        self.combo_res_batch.setCurrentText("1000")
        params_layout.addRow("Batch resolution:", self.combo_res_batch)

        self.combo_relax_batch = QComboBox()
        self.combo_relax_batch.setEditable(True)
        self.combo_relax_batch.addItems(["1000", "1200", "1500"])
        self.combo_relax_batch.setCurrentText("1200")
        params_layout.addRow("Batch relax iterations:", self.combo_relax_batch)

        self.combo_timestep = QComboBox()
        self.combo_timestep.setEditable(True)
        self.combo_timestep.addItems(["0.005", "0.01", "0.002"])
        self.combo_timestep.setCurrentText("0.005")
        params_layout.addRow("Timestep:", self.combo_timestep)

        layout.addWidget(params_group)

        # --- Output ---
        out_group = QGroupBox("Output")
        out_layout = QHBoxLayout(out_group)
        self.edit_output_csv = QLineEdit()
        self.edit_output_csv.setPlaceholderText("Auto: output/sst_master_sweep_results_YYYYMMDD_HHMMSS.csv")
        out_layout.addWidget(self.edit_output_csv)
        self.btn_browse_csv = QPushButton("Browse...")
        self.btn_browse_csv.clicked.connect(self._browse_csv)
        out_layout.addWidget(self.btn_browse_csv)
        layout.addWidget(out_group)

        # --- Progress & log ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(QLabel("Progress:"))
        layout.addWidget(self.progress_bar)

        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setMinimumHeight(120)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.text_log)

        # --- Buttons ---
        btn_row = QHBoxLayout()
        self.btn_start_sweep = QPushButton("Start mass sweep")
        self.btn_start_sweep.setStyleSheet("background-color: #0055ff; color: white; font-weight: bold; padding: 8px;")
        self.btn_start_sweep.clicked.connect(self.start_mass_sweep)
        self.btn_stop_sweep = QPushButton("Stop sweep")
        self.btn_stop_sweep.setStyleSheet("background-color: #aa3333; color: white; padding: 8px;")
        self.btn_stop_sweep.clicked.connect(self.stop_mass_sweep)
        self.btn_stop_sweep.setEnabled(False)
        btn_row.addWidget(self.btn_start_sweep)
        btn_row.addWidget(self.btn_stop_sweep)
        layout.addLayout(btn_row)

        self._sweep_thread = None
        self._sweep_worker = None
        self._on_scope_changed(self.combo_sweep_scope.currentText())

    def _refresh_ab_combo(self):
        self.combo_ab.clear()
        self.combo_ab.addItem("(select AB)", None)
        for display, ab_id in _get_embedded_ab_ids("ideal.txt"):
            self.combo_ab.addItem(display, ab_id)

    def _on_scope_changed(self, text):
        use_selected = "Selected" in text
        self.combo_ab.setEnabled(use_selected)

    def _browse_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save sweep CSV", "", "CSV (*.csv);;All (*)"
        )
        if path:
            self.edit_output_csv.setText(path)

    def log(self, msg: str):
        self.text_log.append(msg)
        # Keep log from growing unbounded
        doc = self.text_log.document()
        if doc.blockCount() > 2000:
            cursor = self.text_log.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.movePosition(cursor.Down, cursor.KeepAnchor, 500)
            cursor.removeSelectedText()
            cursor.deletePreviousChar()

    def start_mass_sweep(self):
        if sstcore is None:
            self.log("[!] sstcore engine not available.")
            return
        if run_master_sweep_embedded is None:
            self.log("[!] master_sweep.run_master_sweep_embedded not available.")
            return

        output_csv = self.edit_output_csv.text().strip()
        if not output_csv:
            os.makedirs("output", exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_csv = os.path.join("output", f"sst_master_sweep_results_{ts}.csv")

        scope = self.combo_sweep_scope.currentText()
        selected_ids = None
        if "Selected" in scope:
            ab_id = self.combo_ab.currentData()
            if not ab_id:
                self.log("No AB selected for single-AB sweep.")
                return
            selected_ids = [ab_id]

        try:
            res_cal = int(self.combo_res_cal.currentText())
            relax_cal = int(self.combo_relax_cal.currentText())
            res_batch = int(self.combo_res_batch.currentText())
            relax_batch = int(self.combo_relax_batch.currentText())
            timestep = float(self.combo_timestep.currentText())
        except ValueError as e:
            self.log(f"[!] Invalid parameter: {e}")
            return

        config = {
            "output_csv": output_csv,
            "embedded_name": "ideal.txt",
            "selected_ids": selected_ids,
            "resolution_calibration": res_cal,
            "relax_iterations_calibration": relax_cal,
            "resolution_batch": res_batch,
            "relax_iterations_batch": relax_batch,
            "timestep": timestep,
        }

        self._sweep_thread = QThread(self)
        self._sweep_worker = MassSweepWorker(config)
        self._sweep_worker.moveToThread(self._sweep_thread)

        self._sweep_thread.started.connect(self._sweep_worker.run)
        self._sweep_worker.sig_log.connect(self.log)
        self._sweep_worker.sig_progress.connect(self.on_sweep_progress)
        self._sweep_worker.sig_finished.connect(self.on_sweep_finished)
        self._sweep_worker.sig_error.connect(self.on_sweep_error)

        self._sweep_worker.sig_finished.connect(self._sweep_thread.quit)
        self._sweep_worker.sig_error.connect(self._sweep_thread.quit)
        self._sweep_thread.finished.connect(self._sweep_worker.deleteLater)
        self._sweep_thread.finished.connect(self._sweep_thread.deleteLater)

        self.btn_start_sweep.setEnabled(False)
        self.btn_stop_sweep.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(0)  # indeterminate until first progress
        self.log(f"Starting mass sweep -> {output_csv}")
        self._sweep_thread.start()

    def stop_mass_sweep(self):
        if hasattr(self, "_sweep_worker") and self._sweep_worker is not None:
            self._sweep_worker.cancel()
            self.log("Stop requested for mass sweep...")

    def on_sweep_progress(self, done: int, total: int, current_id: str):
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(done + 1)
        self.log(f"[progress] {done+1}/{total}: {current_id}")

    def on_sweep_finished(self, output_csv: str):
        self.log(f"[+] Sweep finished. CSV saved to {output_csv}")
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.btn_start_sweep.setEnabled(True)
        self.btn_stop_sweep.setEnabled(False)
        self._sweep_worker = None
        self._sweep_thread = None

    def on_sweep_error(self, err_text: str):
        self.log("[!] Sweep error:")
        self.log(err_text)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.btn_start_sweep.setEnabled(True)
        self.btn_stop_sweep.setEnabled(False)
        self._sweep_worker = None
        self._sweep_thread = None
