@echo off
chcp 65001 > nul
title EnglishMaster Quiz Pro - Local Offline App

echo ========================================================
echo    🚀 Khoi dong EnglishMaster Quiz Pro (Local App)
echo ========================================================
echo.
echo Dang kiem tra moi truong Python...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] Khong tim thay Python tren he thong!
    echo Vui long cai dat Python tai: https://www.python.org/
    pause
    exit /b
)

echo Dang khoi dong may chu backend va mo trinh duyet...
echo.

python main.py

pause
