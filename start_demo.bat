@echo off
chcp 65001 >nul
title KHOA LUAN TOT NGHIEP - SMART TOURISM DEMO LAUNCHER
echo =====================================================================
echo    HE THONG TRO LY DU LICH THONG MINH CO DO HUE (AGENTIC SPATIAL RAG)
echo =====================================================================
echo.

echo [1/3] Kiem tra va khoi dong Ollama AI Service...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo     -> Ollama da dang chay san sang trong he thong.
) else (
    echo     -> Dang khoi dong Ollama Local LLM ngam...
    start "Ollama Engine" /MIN ollama serve
    timeout /t 3 /nobreak >nul
)

echo.
echo [2/3] Khoi dong Backend FastAPI (Port 8000)...
start "Backend - FastAPI Tourism Agent" cmd /k "cd /d "%~dp0" && .venv\Scripts\python.exe src/app/main.py"

echo.
echo [3/3] Khoi dong Frontend Web App (Port 5173)...
start "Frontend - Vite React Map Studio" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo =====================================================================
echo    Tat ca cac dich vu da duoc khoi dong!
echo    Dang tu dong mo Trinh duyet den giao dien Demo: http://localhost:5173
echo =====================================================================
timeout /t 5 /nobreak >nul
start http://localhost:5173

exit
