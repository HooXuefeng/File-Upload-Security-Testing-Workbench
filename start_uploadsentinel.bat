@echo off
setlocal
cd /d "%~dp0"

where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw -3 "%~dp0uploadsentinel_qt.py"
    exit /b 0
)

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "%~dp0uploadsentinel_qt.py"
    exit /b 0
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%~dp0uploadsentinel_qt.py"
    pause
    exit /b %errorlevel%
)

python "%~dp0uploadsentinel_qt.py"
pause
