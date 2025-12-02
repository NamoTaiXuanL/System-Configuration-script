@echo off

:: Python installation script for Windows
:: Downloads and installs Python 3.13.8 with silent installation
:: Project Name Project Group Author Seraphiel 2025-12-02 v1.0

echo === Python 3.13.8 Installation Script ===
echo.

:: Check admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Need administrator rights
    echo Please run as administrator
    pause
    exit /b 1
)

echo Checking current Python versions...
python --version 2>nul && echo Current Python: && python --version
echo.

:: Set variables
set PYTHON_URL=https://www.python.org/ftp/python/3.13.8/python-3.13.8-amd64.exe
set INSTALLER=python-3.13.8-amd64.exe

:: Download Python installer
echo Downloading Python 3.13.8 installer...
if exist "%INSTALLER%" (
    echo Using existing installer: %INSTALLER%
) else (
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%INSTALLER%'"
    if %errorLevel% neq 0 (
        echo ERROR: Download failed. Check internet
        pause
        exit /b 1
    )
    echo Download completed
)

echo.
echo Starting installation...

:: Install Python
"%INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

if %errorLevel% neq 0 (
    echo ERROR: Installation failed, code: %errorLevel%
    echo Trying simple install...
    "%INSTALLER%" /quiet
    if %errorLevel% neq 0 (
        echo ERROR: Complete failure, code: %errorLevel%
        pause
        exit /b 1
    )
)

echo Installation completed
echo.

:: Verify installation
echo Verifying installation...
timeout /t 2 /nobreak >nul

python --version
if %errorLevel% neq 0 (
    echo ERROR: Python verification failed
    pause
    exit /b 1
)

echo.
python -c "print('Hello from Python 3.13.8!')"
echo.

:: Cleanup
echo Cleaning up...
if exist "%INSTALLER%" del "%INSTALLER%"

echo.
echo SUCCESS: Python 3.13.8 installed!
echo Environment variables configured
echo.
echo Usage:
echo   python -c "print('Hello World')"
echo   python --version

pause