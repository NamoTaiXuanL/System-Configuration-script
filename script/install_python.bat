@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Python 3.14.0 Auto Installation Script
:: Features: Detect, Download, Install, Verify

echo ============================================
echo    Python 3.14.0 Auto Installation Script
echo ============================================
echo.

:: 1. Check if Python is already installed
echo [1/5] Checking Python installation status...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python is already installed, version info:
    python --version
    echo.
    set /p choice="Reinstall Python? (y/N): "
    if /i not "!choice!"=="y" (
        echo Installation cancelled.
        pause
        exit /b 0
    )
)

:: 2. Set variables
set "PYTHON_URL=https://www.python.org/ftp/python/3.14.0/python-3.14.0-amd64.exe"
set "INSTALLER_FILE=%TEMP%\python-3.14.0-amd64.exe"

:: 3. Download Python installer
echo [2/5] Downloading Python 3.14.0...
echo Downloading from: %PYTHON_URL%
echo Saving to: %INSTALLER_FILE%
echo.

:: Use PowerShell for download (more reliable)
powershell -Command "try { Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%INSTALLER_FILE%' -UseBasicParsing; Write-Host 'Download successful' -ForegroundColor Green } catch { Write-Host 'Download failed:' $_.Exception.Message -ForegroundColor Red; exit 1 }"

if not exist "%INSTALLER_FILE%" (
    echo Download failed, please check your network connection.
    pause
    exit /b 1
)

echo Download completed!
echo.

:: 4. Silent install Python
echo [3/5] Installing Python...
echo Installation parameters:
echo   - Install path: C:\Python314
echo   - Add to PATH: Yes
echo   - Install pip: Yes
echo.

"%INSTALLER_FILE%" /quiet InstallAllUsers=1 TargetDir="C:\Python314" PrependPath=1 Include_test=0

if %errorlevel% neq 0 (
    echo Installation failed! Error code: %errorlevel%
    pause
    exit /b 1
)

echo Installation completed!
echo.

:: 5. Refresh environment variables
echo [4/5] Refreshing environment variables...

:: Notify system about environment variable changes
echo @echo off > "%TEMP%\refresh_env.bat"
echo :: Refresh environment variables >> "%TEMP%\refresh_env.bat"
echo setx PATH "%PATH%" >nul 2>&1 >> "%TEMP%\refresh_env.bat"
echo if defined SYSTEMROOT ( >> "%TEMP%\refresh_env.bat"
echo     for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul ^| findstr PATH') do set "SYSTEM_PATH=%%B" >> "%TEMP%\refresh_env.bat"
echo     set "PATH=!SYSTEM_PATH!;!PATH!" >> "%TEMP%\refresh_env.bat"
echo ^) >> "%TEMP%\refresh_env.bat"

:: Execute environment variable refresh
call "%TEMP%\refresh_env.bat"

:: Force refresh PATH variable
set "PATH=C:\Python314;C:\Python314\Scripts;%PATH%"

echo Environment variables refreshed.
echo.

:: 6. Test installation
echo [5/5] Verifying Python installation...

:: Wait a moment for environment variables to take effect
timeout /t 3 /nobreak >nul

:: Test Python command
"C:\Python314\python.exe" --version
if %errorlevel% equ 0 (
    echo [SUCCESS] Python installed successfully!

    :: Test pip
    "C:\Python314\Scripts\pip.exe" --version
    if %errorlevel% equ 0 (
        echo [SUCCESS] pip installed successfully!
    ) else (
        echo [WARNING] pip may need manual configuration.
    )

    echo.
    echo ============================================
    echo         Installation Completed!
    echo ============================================
    echo.
    echo Python 3.14.0 has been successfully installed to: C:\Python314
    echo Added to system PATH environment variable.
    echo.
    echo Please reopen Command Prompt to use the new PATH settings.
    echo Or run directly: C:\Python314\python.exe
    echo.
) else (
    echo [ERROR] Python installation verification failed, please check installation logs.
    echo You may need to restart your computer for environment variables to take effect.
)

:: 7. Clean up temporary files
if exist "%INSTALLER_FILE%" (
    echo.
    echo Cleaning up temporary files...
    del "%INSTALLER_FILE%" >nul 2>&1
)

echo.
pause
exit /b 0