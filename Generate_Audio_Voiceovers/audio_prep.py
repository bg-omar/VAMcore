import torch
import torchaudio
import torchaudio.transforms as T

def optimize_audio_for_xtts(input_path: str, output_path: str):
    print(f"[I/O] Inlezen van ruw audiobestand: {input_path}")
    waveform, sample_rate = torchaudio.load(input_path)

    # 1. Kanaal Reductie (Stereo naar Mono)
    if waveform.size(0) > 1:
        print("[Signaal] Stereo gedetecteerd. Neerwaartse menging (downmix) naar Mono...")
        # Gemiddelde over de kanaal-dimensie
        waveform = torch.mean(waveform, dim=0, keepdim=True)
    else:
        print("[Signaal] Bestand is reeds Mono.")

    # 2. Frequentie Transformatie (Resampling)
    target_sample_rate = 22050
    if sample_rate != target_sample_rate:
        print(f"[Signaal] Resampling van {sample_rate} Hz naar {target_sample_rate} Hz...")
        resampler = T.Resample(orig_freq=sample_rate, new_freq=target_sample_rate)
        waveform = resampler(waveform)
    else:
        print(f"[Signaal] Sample rate is reeds de canonieke {target_sample_rate} Hz.")

    # 3. Amplitude Normalisatie (Peak Normalization)
    print("[Signaal] Toepassen van Peak Normalization...")
    # Voorkom divisie door nul
    peak_amplitude = torch.max(torch.abs(waveform))
    if peak_amplitude > 0:
        waveform = waveform / peak_amplitude

    # Optioneel: Schaal lichtjes terug om clipping in DAC's te voorkomen (Headroom)
    waveform = waveform * 0.95

    # 4. Exporteren
    torchaudio.save(output_path, waveform, target_sample_rate, encoding="PCM_S", bits_per_sample=16)
    print(f"[I/O] Geoptimaliseerd bestand weggeschreven naar: {output_path}")

if __name__ == "__main__":
    ruwe_bestand = "ruwe_opname.wav"       # Vervang dit door uw bestandsnaam
    geoptimaliseerd_bestand = "my_voice.wav" # Dit bestand voert u aan XTTS

    optimize_audio_for_xtts(ruwe_bestand, geoptimaliseerd_bestand)