@echo off
cd /d %~dp0
if not exist logs mkdir logs

echo [INFO] Installing dependencies...
python -m pip install -r requirements.txt > logs\install.log 2>&1
if errorlevel 1 (
  echo [ERROR] Dependency installation failed. See logs\install.log
  pause
  exit /b 1
)

echo [INFO] Starting app...
python -m streamlit run app.py --server.headless=true > logs\app.log 2>&1

echo [INFO] App exited. See logs\app.log for details.
pause
