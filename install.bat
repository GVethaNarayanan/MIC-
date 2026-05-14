@echo off
echo =====================================================
echo   MIC Translator Dashboard — Dependency Installer
echo =====================================================
echo.

:: Check Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found. Please install Python 3.9+ and try again.
    pause
    exit /b 1
)

echo [1/4] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [2/4] Installing PyAudio (binary wheel)...
python -m pip install pipwin
pipwin install pyaudio

echo.
echo [3/4] Installing all Python requirements...
python -m pip install -r requirements.txt

echo.
echo [4/4] Checking FFmpeg...
ffmpeg -version >nul 2>&1
IF ERRORLEVEL 1 (
    echo.
    echo [WARN] FFmpeg not found in PATH.
    echo        Whisper AI requires FFmpeg for audio decoding.
    echo        Download from: https://ffmpeg.org/download.html
    echo        Then add ffmpeg\bin to your system PATH.
    echo        (The app will still work using Google SR as fallback)
) ELSE (
    echo [OK] FFmpeg is available.
)

echo.
echo =====================================================
echo   Installation complete!
echo   Run the dashboard with:   run_dashboard.bat
echo =====================================================
pause
