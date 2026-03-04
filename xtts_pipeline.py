import os
import time
import torch

# ==========================================
# PYTORCH BEVEILIGINGS-PATCH VOOR LEGACY MODELLEN
# Forceert backwards compatibility voor Coqui TTS
# ==========================================
_original_load = torch.load
def _legacy_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)
torch.load = _legacy_load
# ==========================================

import torchaudio
import torchaudio.transforms as T
from TTS.api import TTS

# ==========================================
# [1] PRESET CONFIGURATIE
# ==========================================
RUWE_AUDIO_IN    = "ruwe_opname.wav"
GEFILTERDE_AUDIO = "temp_referentie.wav"
AUDIO_UIT        = "mijn_ai_stem.wav"
TAAL             = "en"
TEKST            = "The beige hue on the waters of the loch impressed all, including the French queen, before she heard that symphony again."

TEMPERATUUR      = 0.75
SNELHEID         = 1.0
# ==========================================
def optimize_signal(input_path: str, output_path: str):
    """Zet ruwe audio om naar een wiskundig genormaliseerde mono-tensor van 22050 Hz."""
    print(f"\n[Fase 1] Akoestische Preprocessing: {input_path}")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Kan het invoerbestand '{input_path}' niet vinden. Neem dit bestand op en plaats het in de map.")

    waveform, sample_rate = torchaudio.load(input_path)

    # Kanaalreductie naar Mono
    if waveform.size(0) > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)

    # Nyquist frequentie-transformatie
    target_sr = 22050
    if sample_rate != target_sr:
        resampler = T.Resample(orig_freq=sample_rate, new_freq=target_sr)
        waveform = resampler(waveform)

    # Amplitude Normalisatie (Headroom: 0.95)
    peak = torch.max(torch.abs(waveform))
    if peak > 0:
        waveform = (waveform / peak) * 0.95

    torchaudio.save(output_path, waveform, target_sr, encoding="PCM_S", bits_per_sample=16)
    print(f" -> Signaal geoptimaliseerd en opgeslagen als '{output_path}'.")

def run_synthesis(text: str, ref_audio: str, output_audio: str, lang: str):
    """Laadt het XTTS model in het XPU VRAM en genereert de spraak."""
    print("\n[Fase 2] Neurale Spraaksynthese (XTTSv2)")

    # Native Hardware toewijzing (XPU voor Intel Arc)
    device = "xpu" if (hasattr(torch, 'xpu') and torch.xpu.is_available()) else "cpu"
    print(f" -> Compute engine: {device.upper()}")

    print(" -> Laden van netwerkgewichten...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    print(" -> Start voorwaartse propagatie...")
    t_start = time.time()

    tts.tts_to_file(
        text=text,
        speaker_wav=ref_audio,
        language=lang,
        file_path=output_audio,
        speed=SNELHEID,
        temperature=TEMPERATUUR
    )

    t_delta = time.time() - t_start
    print(f" -> Spraak succesvol gegenereerd in {t_delta:.2f} seconden.")
    print(f"\n[I/O Voltooid] Resultaat bevindt zich in: {output_audio}")

if __name__ == "__main__":
    try:
        optimize_signal(RUWE_AUDIO_IN, GEFILTERDE_AUDIO)
        run_synthesis(TEKST, GEFILTERDE_AUDIO, AUDIO_UIT, TAAL)
    except Exception as e:
        print(f"\n[Fatale Fout] Pipeline afgebroken: {e}")