@echo off
cd /d %~dp0

REM Step 1: Build EXE bundle with PyInstaller
python -m pip install -r requirements.txt
pyinstaller --noconfirm --clean --name CaseManagerLauncher launcher.py

REM Step 2: Build installer with Inno Setup (requires iscc in PATH)
iscc installer\CaseManagerSetup.iss

echo.
echo Done.
echo EXE bundle: dist\CaseManagerLauncher\CaseManagerLauncher.exe
echo Installer : dist_installer\CaseManagerSetup.exe
pause
