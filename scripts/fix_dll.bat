@echo off
echo 🔧 DLL sorununu cozmeye calisiyorum...

REM Install Microsoft Visual C++ Redistributable dependencies
echo 📦 Visual C++ runtime yukluyor...
winget install Microsoft.VCRedist.2015+.x64

REM Recompile DLL with correct flags
echo 🔨 DLL yeniden derleniyor...
g++ -shared -o sunoready_audio.dll sunoready_audio.cpp -std=c++17 -O2 -Wl,--subsystem,windows

echo ✅ DLL duzeltildi! Uygulamayi yeniden baslatiniz.
pause
