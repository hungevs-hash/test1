@echo off
setlocal
cd /d %~dp0

set "OUT_DIR=dist_zip"
set "PKG_DIR=%OUT_DIR%\CaseManager"
set "ZIP_FILE=%OUT_DIR%\CaseManager_portable.zip"

if not exist %OUT_DIR% mkdir %OUT_DIR%
if exist %PKG_DIR% rmdir /s /q %PKG_DIR%
mkdir %PKG_DIR%

copy app.py %PKG_DIR%\ >nul
copy launcher.py %PKG_DIR%\ >nul
copy run_app.bat %PKG_DIR%\ >nul
copy run_portable.bat %PKG_DIR%\ >nul
copy requirements.txt %PKG_DIR%\ >nul
copy README.md %PKG_DIR%\ >nul
if exist docs xcopy docs %PKG_DIR%\docs\ /E /I /Y >nul
if exist scripts xcopy scripts %PKG_DIR%\scripts\ /E /I /Y >nul

powershell -NoProfile -Command "Compress-Archive -Path '%PKG_DIR%\\*' -DestinationPath '%ZIP_FILE%' -Force"
if errorlevel 1 (
  echo [ERROR] Failed to create zip package.
  exit /b 1
)

echo [OK] Portable package created: %ZIP_FILE%
endlocal
