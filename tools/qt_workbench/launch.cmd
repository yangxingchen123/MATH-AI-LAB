@echo off
setlocal
pushd "%~dp0..\.."
set "LOG=%TEMP%\math-ai-lab-qt-launch.log"
set "PROBE=%TEMP%\math-ai-lab-pyexe.txt"
>>"%LOG%" echo %DATE% %TIME% launch.cmd cwd=%CD%

set "PYEXE="
call :try_py
if not defined PYEXE call :try_python
if not defined PYEXE goto no_python

set "RUN=%PYEXE:python.exe=pythonw.exe%"
if not exist "%RUN%" set "RUN=%PYEXE%"
>>"%LOG%" echo %DATE% %TIME% start %RUN%
start "" /D "%CD%" "%RUN%" -m tools.qt_workbench launch
popd
exit /b 0

:try_py
where py >nul 2>&1 || exit /b 0
py -3 -c "import PySide6,sys;print(sys.executable)" >"%PROBE%" 2>nul || exit /b 0
set /p PYEXE=<"%PROBE%"
exit /b 0

:try_python
where python >nul 2>&1 || exit /b 0
python -c "import PySide6,sys;print(sys.executable)" >"%PROBE%" 2>nul || exit /b 0
set /p PYEXE=<"%PROBE%"
exit /b 0

:no_python
>>"%LOG%" echo %DATE% %TIME% no python with PySide6
where python >nul 2>&1
if not errorlevel 1 (
  python -c "from tools.qt_workbench.bootstrap import notify_missing_pyside; notify_missing_pyside()"
) else (
  mshta "javascript:alert('Python was not found. Install Python and check Add python.exe to PATH.');close()"
)
popd
exit /b 1
