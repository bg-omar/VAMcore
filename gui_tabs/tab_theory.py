# gui_tabs/tab_theory.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView

try:
    import swirl_string_core as sstcore
except ImportError:
    try:
        import sstbindings as sstcore
    except ImportError:
        sstcore = None


class TabTheory(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Knoppen bovenaan
        btn_theory_console = QPushButton("Print Derivation to Console")
        btn_theory_console.clicked.connect(self.print_derivation)
        layout.addWidget(btn_theory_console)

        btn_theory_latex = QPushButton("Show Canonical Density Derivation (LaTeX)")
        btn_theory_latex.setStyleSheet("background-color: #0055ff; color: white; padding: 8px;")
        btn_theory_latex.clicked.connect(self.show_latex_derivation)
        layout.addWidget(btn_theory_latex)

        # --- QWebEngineView ---
        self.math_view = QWebEngineView()
        self.math_html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <style>
                body { background-color: #1e1e1e; color: #d4d4d4; font-family: sans-serif; padding: 15px; }
                ::-webkit-scrollbar { width: 10px; }
                ::-webkit-scrollbar-track { background: #1e1e1e; }
                ::-webkit-scrollbar-thumb { background: #555; }
            </style>
        </head>
        <body>
            <div id="content"><p><i>Press the blue button above to render equations...</i></p></div>
            <script>
                function renderMath(latexString) {
                    document.getElementById('content').innerHTML = latexString;
                    MathJax.typesetPromise();
                }
            </script>
        </body>
        </html>
        """
        self.math_view.setHtml(self.math_html_template)
        layout.addWidget(self.math_view)

    def print_derivation(self):
        if sstcore is None:
            print("[!] sstcore engine not available.")
            return
        try:
            sstcore.ParticleEvaluator.print_canonical_derivation()
        except Exception as e:
            print(f"[!] Function not found. ({e})")

    def show_latex_derivation(self):
        latex_content = r"""
        <h2>SST Canon: Dynamische Sluiting van de Kerndichtheid</h2>
        <p>In de Swirl-String Theory (SST) wordt de effectieve massadichtheid van de vortexkern, \(\rho_{\text{core}}\), strict afgeleid als een dynamische sluitingsrelatie. De maximale tangentiële spanning is in exact evenwicht met de hydrodynamische traagheid van het interne fluïdum.</p>

        <p>Door de maximale swirl-kracht \(F_{\!\boldsymbol{\circlearrowleft}}^{\max}\) te verdelen over de effectieve dwarsdoorsnede van de Rankine-kern \(A = \pi r_c^2\), volgt de dichtheid direct uit de continue vloeistofmechanica:</p>

        \[ \rho_{\text{core}} = \frac{F_{\!\boldsymbol{\circlearrowleft}}^{\max}}{\pi r_c^2 \lVert \mathbf{v}_{\!\boldsymbol{\circlearrowleft}}\rVert^2} \]

        <p>Deze formulering verankert de volgende harde, parameter-vrije sluitingsrelatie voor de fundamenten van de theorie:</p>

        $$ F_{\!\boldsymbol{\circlearrowleft}}^{\max} - \rho_{\text{core}}\lVert \mathbf{v}_{\!\boldsymbol{\circlearrowleft}}\rVert^2 \pi r_c^2 = 0 $$

        <h3>Canonieke Constanten (Evaluatie)</h3>
        <ul>
            <li>\( F_{\!\boldsymbol{\circlearrowleft}}^{\max} = 29.053507 \text{ N} \)</li>
            <li>\( r_c = 1.40897017 \times 10^{-15} \text{ m} \)</li>
            <li>\( \lVert \mathbf{v}_{\!\boldsymbol{\circlearrowleft}}\rVert = 1.09384563 \times 10^6 \text{ m s}^{-1} \)</li>
        </ul>

        <p>De evaluatie resulteert in de exacte parameters:</p>

        $$ \rho_{\text{core}} = 3.8934358266918687 \times 10^{18} \text{ kg m}^{-3} $$
        $$ \rho_{\!E} = \rho_{\text{core}} c^2 = 3.49924561231878 \times 10^{35} \text{ J m}^{-3} $$
        """
        safe_content = latex_content.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
        js_code = f'renderMath("{safe_content}");'
        self.math_view.page().runJavaScript(js_code)
        print("[*] LaTeX Derivation Rendered.")
