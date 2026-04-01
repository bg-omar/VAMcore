import torch
import intel_extension_for_pytorch as ipex
from TTS.api import TTS
import time

def main():
    # 1. Hardware Enumeratie en Tensor Routering
    if hasattr(ipex, 'has_xpu') and ipex.has_xpu():
        device = torch.device("xpu")
        print(f"[Compute] Tensor-operaties gerouteerd naar: {ipex.xpu.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        print("[Waarschuwing] SYCL/XPU niet gedetecteerd. Fallback naar host-CPU.")

    # 2. VRAM Allocatie voor het XTTSv2 Model
    print("[Model] Laden van XTTSv2 via Coqui TTS API...")
    # Opmerking: de eerste keer runnen zal het model downloaden (~1.8 GB)
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

    # Verplaats de transformatorgewichten naar de Intel GPU
    tts.to(device)

    # 3. Synthese Parameters
    text_to_synthesize = "This is a strictly English text-to-speech generation, accelerated by my Intel Arc discrete graphics."

    # ZORG DAT DIT BESTAND BESTAAT:
    # Vereisten: Mono kanaal, 22050 Hz of 48000 Hz, ruisvrij, exact uw stem, 3 tot 10 seconden lang.
    reference_audio_path = "referentie_stem_engels.wav"
    output_path = "synthese_resultaat_xpu.wav"

    # 4. Inferentie en Prestatie-evaluatie
    print("[Synthese] Autoregressieve generatie gestart...")
    t_start = time.time()

    # De forward pass voor extractie van de speaker-embedding en spraaksynthese
    tts.tts_to_file(
        text=text_to_synthesize,
        speaker_wav=reference_audio_path,
        language="en",
        file_path=output_path
    )

    t_delta = time.time() - t_start
    print(f"[Synthese] Voltooid in {t_delta:.3f} seconden.")
    print(f"[I/O] Resultaat weggeschreven naar: {output_path}")

if __name__ == "__main__":
    main()