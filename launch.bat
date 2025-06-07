@echo off
cls
color 0A
title SunoReady - Audio Processing Tool Launcher

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║         SunoReady Audio Processor        ║
echo  ║              Starting...                 ║
echo  ╚══════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python bulunamadi! Lutfen Python 3.11+ yukleyin.
    echo    https://python.org/downloads
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo ⏳ Bagimliliklar kontrol ediliyor...
python -c "import customtkinter, librosa, yt_dlp" >nul 2>&1
if errorlevel 1 (
    echo ❌ Eksik bagimliliklar tespit edildi!
    echo 🔧 Bagimliliklar otomatik yukleniyor...
    pip install -r requirements.txt
)

echo ✅ Bagimliliklar OK!
echo 🚀 SunoReady baslatiliyor...
echo.
echo Terminal konsolu icin 'Show Terminal' butonunu kullanin!
echo.

REM Start application without console window
start "" /B pythonw app.py

echo ✨ Uygulama baslatildi! GUI penceresi acilmasi icin bekleyin...
timeout /t 2 /nobreak >nul
exit
