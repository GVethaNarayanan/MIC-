@echo off
echo =====================================================
echo   MIC Translator Dashboard — Starting...
echo =====================================================
echo.
echo  Dashboard URL: http://localhost:8501
echo  Press Ctrl+C to stop the server.
echo.
cd /d "%~dp0"
streamlit run app.py --server.port 8501 --server.headless false --theme.base dark
pause
