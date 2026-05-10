@echo off
cd /d %~dp0
if not exist dist\CaseManagerLauncher\CaseManagerLauncher.exe (
  echo [ERROR] Portable EXE not found. Please run build_exe.bat first.
  pause
  exit /b 1
)

start "Case Manager" dist\CaseManagerLauncher\CaseManagerLauncher.exe
