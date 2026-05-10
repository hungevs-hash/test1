@echo off
cd /d %~dp0
python -m pip install -r requirements.txt
pyinstaller --noconfirm --clean --name CaseManagerLauncher launcher.py

echo.
echo Build done. EXE output:
echo dist\CaseManagerLauncher\CaseManagerLauncher.exe
pause
