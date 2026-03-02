@echo off
echo === [A] Activeren van Conda Omgeving ===
call C:\Users\mr\anaconda3\Scripts\activate.bat SSTcore12

echo === [B] Driver-Niveau Isolatie (Level Zero) ===
:: Forceer de fysieke driver om uitsluitend apparaat 0 (Arc A770) te indexeren
set ZE_AFFINITY_MASK=0
set ONEAPI_DEVICE_SELECTOR=level_zero:gpu
set SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS=1

echo === [C] Starten van Hardware Validatie ===
python verify_sst_hardware.py

pause