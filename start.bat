@echo off
chcp 65001 >nul

rem ---- Имя процесса без .exe ----
set "PROC=Internal Event Receiver"

tasklist /FI "IMAGENAME eq %PROC%.exe" | find /I "%PROC%.exe" >nul
if %ERRORLEVEL%==0 (
    echo Процесс уже запущен. Выходим.
    exit /b 0
)

rem ---- Запуск твоего exe ----
start "" "%~dp0main.exe"
