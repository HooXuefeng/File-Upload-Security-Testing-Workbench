@echo off
setlocal
cd /d "%~dp0"
echo UploadSentinel debug launcher
echo.
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%~dp0uploadsentinel_qt.py"
) else (
    python "%~dp0uploadsentinel_qt.py"
)
echo.
echo Exit code: %errorlevel%
pause
