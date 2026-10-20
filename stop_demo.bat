@echo off
chcp 65001 >nul
title KHOA LUAN TOT NGHIEP - STOP SERVICES
echo =====================================================================
echo    DANG DONG TOAN BO CAC TIEN TRINH DEMO (Backend, Frontend, Ollama)...
echo =====================================================================
echo.

taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul
taskkill /F /IM ollama.exe /T 2>nul

echo.
echo -> Da dong tat ca cac tien trinh thanh cong!
echo.
pause
