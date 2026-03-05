@echo off
echo === [A] Initialiseren van Conda Omgeving ===
call C:\Users\mr\anaconda3\Scripts\activate.bat SSTcore11

echo === [B] Initialiseren van Intel oneAPI Runtimes ===
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo === [C] Configureren van Level Zero (Arc GPU Optimalisaties) ===
:: Vereist voor PyTorch 2.4+ op Xe-HPG architectuur om asynchrone commandlijsten te forceren
set SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS=1
:: Activeert System Management voor hardware enumeratie
set ZES_ENABLE_SYSMAN=1

echo === [D] Starten van Hardware Validatie ===
python verify_sst_hardware.py

pause