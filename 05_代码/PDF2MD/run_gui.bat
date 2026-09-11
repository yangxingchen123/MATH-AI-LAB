@echo off
cd /d "%~dp0"
REM Do not run PowerShell here: Win11 Windows Terminal would flash an empty window.
REM Refresh PDF2MD.lnk separately via scripts\ensure_shortcut.ps1 (install / first setup).

if exist "%~dp0.venv\Scripts\pythonw.exe" (
  start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0run_gui.py"
  exit /b 0
)
where pythonw >nul 2>nul
if %ERRORLEVEL%==0 (
  start "" pythonw "%~dp0run_gui.py"
  exit /b 0
)
echo pythonw.exe not found. Use the project .venv or install Python with pythonw.exe.
echo Do not launch with python.exe — that keeps an empty console attached.
pause
exit /b 1
