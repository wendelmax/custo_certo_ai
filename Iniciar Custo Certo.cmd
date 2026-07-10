@echo off
title Custo Certo AI
cd /d "%~dp0"
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "%~dp0run.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocorreu um erro. Pressione qualquer tecla para sair.
    pause >nul
)
