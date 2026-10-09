@echo off
echo ============================================
echo   Food Hub Bot: Instalacion
echo ============================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado.
    echo Descargalo desde https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH"
    pause
    exit /b 1
)

echo [1/3] Instalando dependencias...
pip install -r "%~dp0requirements.txt" --quiet
if errorlevel 1 (
    echo [ERROR] Fallo al instalar camoufox
    pause
    exit /b 1
)

echo [2/3] Descargando navegador Camoufox...
python -m camoufox fetch
if errorlevel 1 (
    echo [ERROR] Fallo al descargar el navegador
    pause
    exit /b 1
)

echo [3/3] Instalacion completada.
echo.
echo ============================================
echo   Listo! Ejecuta run.bat para iniciar el bot
echo ============================================
echo.
pause
