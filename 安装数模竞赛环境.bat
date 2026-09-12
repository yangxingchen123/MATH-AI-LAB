@echo off
chcp 65001 >nul
cd /d "%~dp0"

where py >nul 2>&1 && (
  py -3 -m pip install -r tools\modeling\requirements-contest.txt
  if errorlevel 1 goto fail
  py -3 -m tools.modeling contest-smoke
  if errorlevel 1 goto fail
  exit /b 0
)

where python >nul 2>&1 && (
  python -m pip install -r tools\modeling\requirements-contest.txt
  if errorlevel 1 goto fail
  python -m tools.modeling contest-smoke
  if errorlevel 1 goto fail
  exit /b 0
)

echo 找不到 Python。请安装后勾选 Add python.exe to PATH。
pause
exit /b 1

:fail
echo 数模竞赛 sidecar 未能安装或烟雾检查失败。
echo 不要把这些包写进根 requirements.txt。
echo   python -m pip install -r tools\modeling\requirements-contest.txt
echo   python -m tools.modeling contest-smoke
pause
exit /b 1
