@echo off
cd /d "%~dp0"
echo =======================================================
echo 🚀 Iniciando Base de Datos y Dashboard de Hardware...
echo =======================================================
echo.

docker-compose up -d

echo.
echo =======================================================
echo ✅ ¡SISTEMA INICIADO CON EXITO!
echo.
echo 📊 Puedes abrir el Dashboard ingresando a:
echo    http://localhost:8501
echo.
echo =======================================================
pause
