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

REM Check for DLL and compile if needed
echo 🔍 Performance DLL kontrol ediliyor...
if exist sunoready_audio.dll (
    echo ✅ High-performance DLL mevcut!
    echo ⚡ Ultra-fast mode aktif olacak
) else (
    if exist sunoready_audio.cpp (
        echo 🔨 DLL bulunamadi - otomatik compile ediliyor...
        echo 💡 Bu islemi sadece bir kez yapacagiz...
        
        REM Try to compile DLL
        g++ -shared -fPIC -O3 -march=native -DNDEBUG sunoready_audio.cpp -o sunoready_audio.dll -static-libgcc -static-libstdc++ >nul 2>&1
        
        if exist sunoready_audio.dll (
            echo ✅ DLL basariyla compile edildi!
            echo 🚀 High-performance mode hazir!
        ) else (
            echo ⚠️ DLL compile edilemedi - Python mode kullanilacak
            echo 💡 MinGW-w64 yuklemek icin: winget install mingw-w64
        )
    ) else (
        echo ⚠️ DLL source dosyasi bulunamadi - Python mode kullanilacak
    )
)

echo 🚀 SunoReady baslatiliyor...
echo.
echo Terminal konsolu icin 'Show Terminal' butonunu kullanin!
echo.

REM Start application without console window
start "" /B pythonw app.py

echo ✨ Uygulama baslatildi! GUI penceresi acilmasi icin bekleyin...
timeout /t 2 /nobreak >nul
exit
