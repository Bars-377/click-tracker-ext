@echo off
REM Остановка всех процессов nginx
echo Останавливаем Nginx...
powershell -Command "Stop-Process -Name nginx -Force"
echo Nginx остановлен.
pause