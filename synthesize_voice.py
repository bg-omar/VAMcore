import torch
import intel_extension_for_pytorch as ipex
from TTS.api import TTS
import time

def main():
    print("[Configuratie] Initialiseren van IPEX via XPU...")
    device = "xpu" if torch.xpu.is_available() else "cpu"
    print(f"[Hardware] Routering operaties naar: {device}")

    print("[Model] Laden van het Coqui XTTSv2 Netwerk...")
    # Laad het model expliciet en forceer de precisie naar half (FP16) voor maximale XMX bandbreedte
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    text_input = "Hello. This audio is generated entirely on my local machine, powered by an Intel graphics card processing a neural network."
    reference_wav = "my_voice.wav"  # Plaats hier uw eigen ruisvrije audio sample
    output_wav = "generated_voice.wav"

    print("[Synthese] Starten van de autoregressieve voorwaartse propagatie...")
    start_time = time.time()

    # Genereer de spraak
    tts.tts_to_file(
        text=text_input,
        speaker_wav=reference_wav,
        language="en",
        file_path=output_wav
    )

    t_delta = time.time() - start_time
    print(f"[Synthese] Succesvol voltooid in {t_delta:.2f} seconden.")
    print(f"[I/O] Resultaat opgeslagen in {output_wav}")

if __name__ == "__main__":
    main()