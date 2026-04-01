import os
import time
import re
import torch
import torchaudio

# ==========================================
# PYTORCH BEVEILIGINGS-PATCH VOOR LEGACY MODELLEN
# ==========================================
_original_load = torch.load
def _legacy_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)
torch.load = _legacy_load
# ==========================================

from TTS.api import TTS

# ==========================================
# [1] PRESET CONFIGURATIE
# ==========================================
REFERENTIE_AUDIO = "ruwe_opname.wav"   # De Gouden Vector (Take 005 / 002)
AUDIO_UIT        = "SST_Audioboek.wav" # De geëxporteerde lange podcast
TAAL             = "en"
TEMPERATUUR      = 0.80
SNELHEID         = 1.05

# De stilte (in seconden) die de AI tussen twee afzonderlijke zinnen voegt
PAUZE_TUSSEN_ZINNEN = 0.5

LANGE_TEKST = """
We present Version 0.7.8 of the Swirl-String Theory, or SST, Canon. 
This release unifies three historically distinct phenomena: time, gravity, and mass, into a single hydrodynamic framework based on a frictionless, incompressible superfluid condensate. 
We resolve the "Problem of Time" in quantum mechanics by defining time as a relational observable, or event count, derived from a conserved topological current, J mu. 
We demonstrate that the scalar field mediating this clock synchronization satisfies a Poisson equation, naturally yielding the inverse-square law for gravity without assuming curved spacetime. 
Finally, we derive the invariant masses of stable particles, such as protons and electrons, as the integrated swirl energy of topological knots. 
This strictly enforces the separation between the vacuum fluid density, rho f, roughly ten to the power of minus seven kilograms per cubic meter, and the core condensate density, rho core, roughly ten to the power of eighteen kilograms per cubic meter.
"""
# ==========================================

def text_to_chunks(text: str, max_chars: int = 200) -> list:
    """Knipt een document in zinnen, en fragmenteert verder op komma's indien nodig."""
    clean_text = " ".join(text.split())
    # 1. Primaire splitsing op hoofd-leestekens
    raw_chunks = re.split(r'(?<=[.!?])\s+', clean_text)

    final_chunks = []
    for chunk in raw_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        # Als de zin binnen de limiet past, direct toevoegen
        if len(chunk) <= max_chars:
            final_chunks.append(chunk)
        else:
            # 2. Secundaire splitsing op komma's of puntkomma's
            sub_chunks = re.split(r'(?<=[,;])\s+', chunk)
            huidige_zin = ""

            for sub in sub_chunks:
                # Controleer of de toevoeging de limiet overschrijdt
                if len(huidige_zin) + len(sub) < max_chars:
                    huidige_zin += sub + " "
                else:
                    if huidige_zin:
                        final_chunks.append(huidige_zin.strip())
                    huidige_zin = sub + " "

            if huidige_zin:
                final_chunks.append(huidige_zin.strip())

    return final_chunks

def synthesize_long_audio():
    print("\n=== [Fase 1] Tekst Segmentatie ===")
    zinnen = text_to_chunks(LANGE_TEKST)
    print(f" -> Document succesvol opgeknipt in {len(zinnen)} sequentiële zinnen.")

    print("\n=== [Fase 2] Neurale Spraaksynthese (XTTSv2) ===")
    device = "xpu" if (hasattr(torch, 'xpu') and torch.xpu.is_available()) else "cpu"
    print(f" -> Compute engine geselecteerd: {device.upper()}")

    print(" -> Laden van XTTS netwerkgewichten in VRAM...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    # Pre-allocatie van de stilte-tensor (0.5 seconden = 11025 samples bij 22050 Hz)
    sample_rate = 22050
    silence_samples = int(PAUZE_TUSSEN_ZINNEN * sample_rate)
    silence_list = [0.0] * silence_samples

    geaccumuleerde_audio = []
    totale_tijd = time.time()

    print("\n -> Starten van iteratieve voorwaartse propagatie:")
    for i, zin in enumerate(zinnen):
        print(f"    [{i+1}/{len(zinnen)}] Synthetiseren: '{zin[:40]}...'")

        # tts.tts() retourneert direct een lijst van floats (de audiogolfvorm)
        wav = tts.tts(
            text=zin,
            speaker_wav=REFERENTIE_AUDIO,
            language=TAAL,
            speed=SNELHEID,
            temperature=TEMPERATUUR
        )

        # Voeg de gegenereerde audio en de rustpauze toe aan de master list
        geaccumuleerde_audio.extend(wav)
        geaccumuleerde_audio.extend(silence_list)

        if device == "xpu":
            torch.xpu.synchronize() # Voorkom asynchrone VRAM overbelasting

    # Conversie naar PyTorch Tensor (1D -> 2D [1, N])
    print("\n=== [Fase 3] Audio Assemblage & Export ===")
    audio_tensor = torch.tensor(geaccumuleerde_audio).unsqueeze(0)

    # L-inf Normalisatie om clipping in het eindbestand te voorkomen
    peak = torch.max(torch.abs(audio_tensor))
    if peak > 0:
        audio_tensor = (audio_tensor / peak) * 0.95

    torchaudio.save(AUDIO_UIT, audio_tensor, sample_rate, encoding="PCM_S", bits_per_sample=16)

    verstreken_tijd = time.time() - totale_tijd
    audio_duur = len(geaccumuleerde_audio) / sample_rate
    print(f" -> Operatie succesvol voltooid in {verstreken_tijd:.2f} s computertijd.")
    print(f" -> Gegenereerde audiolooptijd: {audio_duur:.2f} seconden.")
    print(f"\n[Succes] Audioboek weggeschreven naar: {AUDIO_UIT}")

if __name__ == "__main__":
    synthesize_long_audio()