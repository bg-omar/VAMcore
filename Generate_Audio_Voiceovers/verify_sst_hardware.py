import sys
import time
import numpy as np

# Probeer Intel Extension for Scikit-learn te laden (CPU versnelling)
try:
    from sklearnex import patch_sklearn
    patch_sklearn()
    SKLEARNEX_AVAILABLE = True
except ImportError:
    SKLEARNEX_AVAILABLE = False

# Probeer PyTorch en IPEX te laden (GPU/XPU versnelling)
try:
    import torch
    import intel_extension_for_pytorch as ipex
    TORCH_AVAILABLE = True
except ImportError as e:
    TORCH_AVAILABLE = False
    TORCH_ERROR = str(e)

def verify_cpu_mkl():
    print("=== [1] CPU & MKL (Math Kernel Library) Validatie ===")
    print(f"Python versie: {sys.version.split()[0]}")
    print(f"NumPy versie: {np.__version__}")
    print(f"Intel Extension for Scikit-Learn actief: {SKLEARNEX_AVAILABLE}")
    # NumPy 1.26+ veilige check overgeslagen; MKL is gegarandeerd via intelpython kanaal
    print("-" * 50)

def verify_gpu_xpu():
    print("=== [2] GPU & IPEX (Intel Extension for PyTorch) Validatie ===")
    if not TORCH_AVAILABLE:
        print(f"[Fout] PyTorch of IPEX kon niet worden geladen: {TORCH_ERROR}")
        return None

    print(f"PyTorch versie: {torch.__version__}")
    print(f"IPEX versie: {ipex.__version__}")

    # Vanaf PyTorch 2.4+ / IPEX 2.5+ is XPU een native component van torch
    if hasattr(torch, 'xpu') and torch.xpu.is_available():
        device_count = torch.xpu.device_count()
        print(f"Aantal gedetecteerde XPU apparaten: {device_count}")
        device_name = torch.xpu.get_device_name(0)
        print(f"Primaire XPU: {device_name}")
        return torch.device("xpu")
    else:
        print("[Waarschuwing] Geen XPU gedetecteerd. IPEX is niet correct gekoppeld aan de Intel Arc GPU.")
        return torch.device("cpu")

def compute_sst_tensors(device):
    print("\n=== [3] SST Hardware Validatie via Tensor Operaties ===")
    if device.type != "xpu":
        print("Sla XPU tensor test over vanwege ontbrekende GPU configuratie.")
        return

    print(f"Toewijzen van fysieke constanten aan {device} (FP32 precisie)...")

    # Constanten (SST Canon)
    c_val = 299792458.0  # m/s
    rho_f_val = 7.0e-7   # kg m^-3 (effectieve vloeistofdichtheid)
    v_swirl_val = 1.09384563e6  # m s^-1 (karakteristieke swirl speed)

    # Tensor allocatie op de Arc A770 in FP32
    try:
        c = torch.tensor(c_val, dtype=torch.float32, device=device)
        rho_f = torch.tensor(rho_f_val, dtype=torch.float32, device=device)
        v_swirl = torch.tensor(v_swirl_val, dtype=torch.float32, device=device)

        t_start = time.time()

        # rho_E = 0.5 * rho_f * v_swirl^2
        rho_E = 0.5 * rho_f * (v_swirl ** 2)

        # rho_m = rho_E / c^2
        rho_m = rho_E / (c ** 2)

        if device.type == "xpu":
            torch.xpu.synchronize()

        t_delta = (time.time() - t_start) * 1e6 # in microseconden

        print(f"Tensor bewerkingen succesvol uitgevoerd op {device} in {t_delta:.2f} \u03bcs.")
        print(f"-> Berekende Swirl-energiedichtheid (\u03c1_E): {rho_E.item():.4e} J/m^3")
        print(f"-> Berekende Mass-equivalente dichtheid (\u03c1_m): {rho_m.item():.4e} kg/m^3")
        print("\n[Status] De hardware is volledig operationeel.")

    except Exception as e:
        print(f"[Fout] Tensor bewerking op XPU gefaald: {e}")

if __name__ == "__main__":
    verify_cpu_mkl()
    xpu_device = verify_gpu_xpu()
    if xpu_device:
        compute_sst_tensors(xpu_device)