@echo off
echo === [A] Activeren van Conda Omgeving ===
call C:\Users\mr\anaconda3\Scripts\activate.bat SSTcore_TTS

echo === [B] Asymmetrische Isolatie (Level Zero) ===
:: Selecteer uitsluitend de Arc A770 en negeer de geïntegreerde UHD 770
set ONEAPI_DEVICE_SELECTOR=level_zero:0
set SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS=1
set ZES_ENABLE_SYSMAN=1

echo === [C] Starten van Hardware Validatie ===
::python verify_sst_hardware.py
python xtts_pipeline.py
::python audio_prep.py

pause