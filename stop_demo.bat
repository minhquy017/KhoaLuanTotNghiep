@echo off
chcp 65001 >nul
title KHOA LUAN TOT NGHIEP - STOP SERVICES
echo =====================================================================
echo    DANG DONG CAC TIEN TRINH DEMO (Backend :8000, Frontend :5173)...
echo =====================================================================
echo.

REM Dong tien trinh FastAPI Backend dang lang nghe tren cong 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo -> Dang dong Backend Server (PID: %%a)...
    taskkill /F /PID %%a /T 2>nul
)

REM Dong tien trinh Vite Frontend dang lang nghe tren cong 5173
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173 " ^| findstr "LISTENING"') do (
    echo -> Dang dong Frontend Vite (PID: %%a)...
    taskkill /F /PID %%a /T 2>nul
)

REM Giai phong mo hinh khoi VRAM cua Ollama
ollama stop qwen2.5vl:7b 2>nul

echo.
echo -> Da dong cac tien trinh Demo thanh cong!
echo.
pause
