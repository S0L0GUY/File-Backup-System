@echo off
:: Check for admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    cd /d "%~dp0"
    python main.py
) else (
    :: Relaunch as admin
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
)
