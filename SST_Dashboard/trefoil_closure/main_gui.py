import sys
import os
import glob
import numpy as np
from scipy.optimize import minimize
from setuptools import setup, Extension

# WebEngine stabiliteits-fix voor bepaalde GPU's
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QThread, pyqtSignal

# --- 1. Automatische Hot-Reload Logica ---
def needs_recompile(cpp_file="sst_core.cpp", module_name="sst_core"):
    if not os.path.exists(cpp_file):
        return False
    compiled_files = glob.glob(f"{module_name}.*")
    binaries = [f for f in compiled_files if f.endswith('.pyd') or f.endswith('.so')]
    if not binaries:
        return True
    latest_binary = max(binaries, key=os.path.getmtime)
    return os.path.getmtime(cpp_file) > os.path.getmtime(latest_binary)

def build_sst_core():
    import pybind11

    # Platform-specifieke compiler flags om MSVC waarschuwingen te voorkomen
    if sys.platform == "win32":
        c_args = ["/O2", "/std:c++14"]
    else:
        c_args = ["-O3", "-std=c++11"]

    ext_modules = [
        Extension(
            "sst_core",
            ["sst_core.cpp"],
            include_dirs=[pybind11.get_include()],
            language="c++",
            extra_compile_args=c_args
        ),
    ]
    sys.argv = ["setup.py", "build_ext", "--inplace"]
    setup(name="sst_core", ext_modules=ext_modules, script_args=["build_ext", "--inplace"])

if needs_recompile():
    print("Re-compilatie van sst_core.cpp gestart...")
    build_sst_core()

import sst_core

# --- 2. SST Canonieke Constanten ---
v_swirl = 1.09384563e6
r_c = 1.40897017e-15
rho_core = 3.8934358266918687e18

Gamma = 2 * np.pi * r_c * v_swirl
alpha = (rho_core * Gamma**2) / (4 * np.pi)

def generate_torus_knot(p, q, R, r, N_points=2000):
    sigma = np.linspace(0, 2 * np.pi, N_points, endpoint=False)
    points = np.zeros((N_points, 3))
    points[:, 0] = (R + r * np.cos(q * sigma)) * np.cos(p * sigma)
    points[:, 1] = (R + r * np.cos(q * sigma)) * np.sin(p * sigma)
    points[:, 2] = -r * np.sin(q * sigma)
    return points

def evaluate_functional(R, r, p, q, N_points=1000):
    points = generate_torus_knot(p, q, R, r, N_points)

    C_N = sst_core.calculate_neumann_self_energy(points, r_c)
    L_K = sst_core.calculate_length(points)
    Wr = sst_core.calculate_writhe(points, r_c)
    U_rep_val = sst_core.calculate_core_repulsion(points, r_c)

    # 5. Buigingsstijfheid (Kromming)
    K_K = sst_core.calculate_curvature_penalty(points)

    beta = alpha * np.log(R / r_c) if R > r_c else 0
    gamma = alpha * r_c
    epsilon = alpha * r_c
    delta = alpha * (r_c ** 2)  # Dimensie: [J m]

    E_C = alpha * C_N
    E_L = beta * L_K
    E_H = gamma * abs(Wr)
    E_rep = epsilon * U_rep_val
    E_kappa = delta * K_K

    E_total = E_C + E_L + E_H + E_rep + E_kappa

    # Let op de extra return waarde E_kappa
    return E_total, E_C, E_L, E_H, E_rep, E_kappa, Wr, C_N, L_K

# --- 3. Reken-Thread ---
class ComputationThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, mode, p, q_list, R_init, r_init):
        super().__init__()
        self.mode = mode
        self.p = p
        self.q_list = q_list
        self.R_init = R_init
        self.r_init = r_init

    def run(self):
        if self.mode == "iterate":
            self.do_iterate()

    def do_iterate(self):
        self.log_signal.emit(rf"Start stabiliteits-analyse. Bereken referentie (Elektron $p=2, q=3$)...")

        def objective(x, current_p, current_q):
            R_val, r_val = x[0] * r_c, x[1] * r_c
            # Met U_rep is er geen keiharde grens meer nodig, we kunnen de ruimte openstellen
            if r_val <= 0.1 * r_c or R_val <= 0.1 * r_c:
                return 1e6
            E_tot, _, _, _, _, _, _, _, _ = evaluate_functional(R_val, r_val, current_p, current_q, N_points=600)
            return E_tot * 1e10

            # Zoek eerst de basis-elektron massa
        x0_base = np.array([self.R_init / r_c, self.r_init / r_c])
        bounds_open = ((0.5, 500.0), (0.5, 200.0)) # Vrijere bounds!

        res_e = minimize(objective, x0_base, args=(2, 3), method='L-BFGS-B', bounds=bounds_open, options={'disp': False, 'ftol': 1e-6})
        if not res_e.success:
            self.log_signal.emit("<span style='color:red;'>Optimalisatie elektron-knoop gefaald.</span>")
            return

        R_e, r_e = res_e.x[0] * r_c, res_e.x[1] * r_c
        E_tot_e, _, _, _, _, _, _, _, _ = evaluate_functional(R_e, r_e, 2, 3, N_points=1500)
        mass_e_kg = E_tot_e / (299792458**2)

        self.log_signal.emit(rf"Elektron basis ($2,3$) gestabiliseerd op $R^* = {res_e.x[0]:.2f}\,r_c$, $r^* = {res_e.x[1]:.2f}\,r_c$.<br>Rustmassa $m_e = {mass_e_kg:.2e} \text{{ kg}}$.")
        self.log_signal.emit(rf"<br>Start iteratie voor Baryon-kandidaten (poloidaal $p={self.p}$)...")

        results = []
        for q in self.q_list:
            self.log_signal.emit(rf"Optimaliseer $({self.p}, {q})$-knoop...")
            x0 = np.array([self.R_init / r_c, self.r_init / r_c])

            res = minimize(objective, x0, args=(self.p, q), method='L-BFGS-B', bounds=bounds_open, options={'disp': False, 'ftol': 1e-6})

            if res.success:
                R_opt, r_opt = res.x[0] * r_c, res.x[1] * r_c
                E_tot, E_C, E_L, E_H, E_rep, Wr, _, _, _ = evaluate_functional(R_opt, r_opt, self.p, q, N_points=1500)
                mass_kg = E_tot / (299792458**2)
                ratio = mass_kg / mass_e_kg

                results.append((q, R_opt/r_c, r_opt/r_c, Wr, mass_kg, ratio))
            else:
                self.log_signal.emit(rf"<span style='color:red;'>Optimalisatie gefaald voor q={q}.</span>")

        table_html = (
            rf"<br><b>Topologische Massa Ratios (SST vs Elektron Basis):</b><br>"
            rf"<table style='width:100%; border-collapse: collapse; text-align: left;'>"
            rf"<tr style='border-bottom: 1px solid #fff;'>"
            rf"<th>Knoop $(p,q)$</th><th>$R^*$</th><th>$r^*$</th><th>Writhe $\mathcal{{H}}$</th><th>Massa (kg)</th><th>Ratio (vs $e^-$)</th><th>Doel (Proton)</th>"
            rf"</tr>"
        )

        for r_data in results:
            q, R_opt, r_opt, Wr, mass_kg, ratio = r_data
            target_str = "<b>1836.15</b>" if self.p == 3 else "-"
            # Highlight as a hit if it's within 10% of the proton ratio
            highlight = "color: #00ff00;" if (self.p == 3 and 1600 < ratio < 2000) else ""

            table_html += (
                rf"<tr style='{highlight}'>"
                rf"<td>$({self.p}, {q})$</td>"
                rf"<td>${R_opt:.2f}$</td>"
                rf"<td>${r_opt:.2f}$</td>"
                rf"<td>${Wr:.2f}$</td>"
                rf"<td>${mass_kg:.2e}$</td>"
                rf"<td><b>${ratio:.1f}$</b></td>"
                rf"<td>{target_str}</td>"
                rf"</tr>"
            )

        table_html += rf"</table><br>"
        self.log_signal.emit(table_html)


# --- 4. Hoofd GUI Applicatie ---
class SSTApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SSTcore - Topologische Generatie Iteratie")
        self.resize(1100, 750)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        control_layout = QHBoxLayout()

        self.p_input = QLineEdit("2")
        self.q_input = QLineEdit("3, 5, 7")
        self.R_input = QLineEdit("100")
        self.r_input = QLineEdit("30")

        control_layout.addWidget(QLabel("Poloidaal (p):"))
        control_layout.addWidget(self.p_input)
        control_layout.addWidget(QLabel("Toroidaal (q):"))
        control_layout.addWidget(self.q_input)
        control_layout.addWidget(QLabel("R init (x r_c):"))
        control_layout.addWidget(self.R_input)
        control_layout.addWidget(QLabel("r init (x r_c):"))
        control_layout.addWidget(self.r_input)

        self.btn_iter = QPushButton("Itereer Generaties (p, q)")
        self.btn_iter.clicked.connect(self.run_iteration)
        control_layout.addWidget(self.btn_iter)

        layout.addLayout(control_layout)

        self.browser = QWebEngineView()
        self.init_browser()
        layout.addWidget(self.browser)

    def init_browser(self):
        html = rf"""
        <!DOCTYPE html>
        <html>
        <head>
          <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
          <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
          <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"
            onload="renderMathInElement(document.body, {{delimiters: [{{left: '$$', right: '$$', display: true}}, {{left: '$', right: '$', display: false}}]}});"></script>
          <style>
            body {{ background-color: #1e1e1e; color: #d4d4d4; font-family: 'Consolas', monospace; font-size: 14px; padding: 15px; }}
            .log-entry {{ margin-bottom: 8px; border-bottom: 1px solid #333; padding-bottom: 8px; }}
            th, td {{ padding: 8px; border-bottom: 1px solid #444; }}
          </style>
        </head>
        <body>
          <div id="output">
            <div class="log-entry">SSTcore Hot-Reload actief. Gereed voor generatie-iteratie.</div>
          </div>
          <script>
            function appendLog(htmlContent) {{
              const div = document.createElement('div');
              div.className = 'log-entry';
              div.innerHTML = htmlContent;
              document.getElementById('output').appendChild(div);
              renderMathInElement(div, {{delimiters: [{{left: '$$', right: '$$', display: true}}, {{left: '$', right: '$', display: false}}]}});
              window.scrollTo(0, document.body.scrollHeight);
            }}
          </script>
        </body>
        </html>
        """
        self.browser.setHtml(html)

    def append_log(self, text):
        js_text = text.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
        self.browser.page().runJavaScript(f"appendLog('{js_text}');")

    def run_iteration(self):
        p = int(self.p_input.text().strip())
        q_strs = self.q_input.text().split(',')
        q_list = [int(q.strip()) for q in q_strs if q.strip().isdigit()]
        R_init = float(self.R_input.text()) * r_c
        r_init = float(self.r_input.text()) * r_c

        self.thread = ComputationThread("iterate", p, q_list, R_init, r_init)
        self.thread.log_signal.connect(self.append_log)
        self.thread.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SSTApp()
    window.show()
    sys.exit(app.exec_())