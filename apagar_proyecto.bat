@echo off
cd /d "%~dp0"
echo =======================================================
echo 🛑 Apagando Base de Datos y Dashboard de Hardware...
echo =======================================================
echo.

docker-compose down

echo.
echo =======================================================
echo ✅ ¡SISTEMA APAGADO CON EXITO!
echo Todos los contenedores se detuvieron correctamente.
echo =======================================================
pause
